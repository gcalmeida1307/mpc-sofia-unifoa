"""Exact, privacy-safe answers for structured knowledge sources.

The regular RAG index is intentionally chunk-based.  That is the right model
for prose, but it is not sufficient for questions such as "how many rows have
status X?": a chunk is only a sample of a table.  This module provides a
small, domain-agnostic table reader used before prose retrieval whenever the
question is an explicit structured-data aggregation.

It is deliberately independent of the LLM.  Counts, filters and source
selection are calculated from the complete current file, then only the
aggregate is sent to the response layer.  Row values (including names,
emails, identifiers and clinical fields) never need to enter the answer.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .ingestion import files_for
from .query_analysis import normalize

STRUCTURED_EXTENSIONS = {".csv", ".xlsx", ".json"}
COUNT_MARKERS = (
    "quantos",
    "quantas",
    "quantidade",
    "numero de",
    "número de",
    "total de",
    "count",
    "how many",
    "cuantos",
    "cuantas",
)
SUMMARY_MARKERS = (
    "resuma",
    "resumo",
    "sumarize",
    "summary",
    "descreva o arquivo",
    "estrutura do arquivo",
    "conteudo do arquivo",
    "conteúdo do arquivo",
)
IGNORED_SOURCE_TERMS = {
    "arquivo",
    "arquivos",
    "documento",
    "documentos",
    "fonte",
    "fontes",
    "base",
    "bases",
    "dados",
    "tabela",
    "planilha",
    "csv",
    "xlsx",
    "json",
}


@dataclass(frozen=True)
class StructuredDocument:
    path: Path
    headers: tuple[str, ...]
    rows: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class StructuredAnswer:
    answer: str
    source: Path
    row_count: int
    matched_count: int | None
    operation: str
    filter_column: str | None = None
    filter_value: str | None = None

    def metadata(self) -> dict[str, Any]:
        """Return safe observability data; never include table rows."""
        return {
            "operation": self.operation,
            "source": self.source.name,
            "row_count": self.row_count,
            "matched_count": self.matched_count,
            "filter_column": self.filter_column,
            "filter_value": self.filter_value,
            "complete_source_read": True,
            "pii_rows_returned": False,
        }


def _read_source(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return re.sub(r"\s+", " ", str(value)).strip()


def _unique_headers(values: list[Any]) -> list[str]:
    headers: list[str] = []
    seen: Counter[str] = Counter()
    for index, value in enumerate(values, start=1):
        label = _clean_cell(value) or f"Coluna {index}"
        key = normalize(label)
        seen[key] += 1
        if seen[key] > 1:
            label = f"{label} ({seen[key]})"
        headers.append(label)
    return headers


def _from_csv(path: Path) -> StructuredDocument | None:
    text = _read_source(path)
    if not text.strip():
        return None
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    rows = [row for row in rows if any(_clean_cell(value) for value in row)]
    if not rows:
        return None
    headers = _unique_headers(rows[0])
    records = tuple(
        {
            headers[index]: _clean_cell(value)
            for index, value in enumerate(row[: len(headers)])
        }
        | {headers[index]: "" for index in range(len(row), len(headers))}
        for row in rows[1:]
    )
    return StructuredDocument(path, tuple(headers), records)


def _from_xlsx(path: Path) -> StructuredDocument | None:
    # Imported lazily so text-only deployments do not pay the openpyxl import
    # cost unless a structured workbook is actually queried.
    from openpyxl import load_workbook

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        sheet_rows: list[tuple[list[str], list[list[Any]]]] = []
        all_headers: list[str] = []
        for sheet in workbook.worksheets:
            values = [list(row) for row in sheet.iter_rows(values_only=True)]
            values = [row for row in values if any(value is not None and str(value).strip() for value in row)]
            if not values:
                continue
            headers = _unique_headers(values[0])
            sheet_rows.append((headers, values[1:]))
            for header in headers:
                if normalize(header) not in {normalize(item) for item in all_headers}:
                    all_headers.append(header)
        if not sheet_rows:
            return None
        records: list[dict[str, str]] = []
        for headers, rows in sheet_rows:
            for row in rows:
                record = {header: "" for header in all_headers}
                record.update(
                    {
                        headers[index]: _clean_cell(value)
                        for index, value in enumerate(row[: len(headers)])
                    }
                )
                if any(record.values()):
                    records.append(record)
        return StructuredDocument(path, tuple(all_headers), tuple(records))
    finally:
        workbook.close()


def _json_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for value in payload.values():
            records = _json_records(value)
            if records:
                return records
        return [payload]
    return []


def _from_json(path: Path) -> StructuredDocument | None:
    try:
        payload = json.loads(_read_source(path))
    except (json.JSONDecodeError, OSError, TypeError):
        return None
    records = _json_records(payload)
    if not records:
        return None
    header_keys = list(dict.fromkeys(str(key) for record in records for key in record))
    headers = _unique_headers(header_keys)
    key_by_header = dict(zip(headers, header_keys))
    normalized_records = tuple(
        {header: _clean_cell(record.get(original)) for header, original in key_by_header.items()}
        for record in records
    )
    return StructuredDocument(path, tuple(headers), normalized_records)


def load_structured_document(path: Path) -> StructuredDocument | None:
    suffix = path.suffix.casefold()
    if suffix not in STRUCTURED_EXTENSIONS or not path.is_file():
        return None
    try:
        if suffix == ".csv":
            return _from_csv(path)
        if suffix == ".xlsx":
            return _from_xlsx(path)
        return _from_json(path)
    except (OSError, ValueError, TypeError):
        return None


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize(value))


def _contains_phrase(text: str, phrase: str) -> bool:
    phrase = normalize(phrase).strip()
    if not phrase:
        return False
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalize(text)) is not None


def _source_match_score(path: Path, question: str) -> float:
    stem = normalize(path.stem).replace("_", " ").replace("-", " ").strip()
    compact_stem = _compact(stem)
    query = normalize(question)
    compact_query = _compact(query)
    if compact_stem and compact_stem in compact_query:
        return 1.0
    query_tokens = [token for token in re.findall(r"[\w]+", query) if len(token) >= 4 and token not in IGNORED_SOURCE_TERMS]
    if not query_tokens:
        return 0.0
    token_score = max(
        (SequenceMatcher(None, compact_stem, _compact(token)).ratio() for token in query_tokens),
        default=0.0,
    )
    stem_tokens = set(re.findall(r"[\w]+", stem)) - IGNORED_SOURCE_TERMS
    overlap = len(stem_tokens & set(query_tokens)) / max(1, len(stem_tokens))
    return max(token_score, overlap)


def _header_value_score(document: StructuredDocument, question: str) -> float:
    query = normalize(question)
    score = 0.0
    for header in document.headers:
        if _contains_phrase(query, header) or _compact(header) in _compact(query):
            score += 0.45
            values = {
                normalize(row.get(header, "")).strip()
                for row in document.rows
                if normalize(row.get(header, "")).strip()
            }
            score += min(0.45, 0.10 * sum(_contains_phrase(query, value) for value in values))
    return min(1.0, score)


def resolve_structured_source(root: Path, module_id: str, question: str) -> StructuredDocument | None:
    """Find the best current table, including approximate filename mentions."""
    candidates: list[tuple[float, StructuredDocument]] = []
    for path in files_for(root, module_id):
        if path.suffix.casefold() not in STRUCTURED_EXTENSIONS:
            continue
        document = load_structured_document(path)
        if document is None:
            continue
        source_score = _source_match_score(path, question)
        content_score = _header_value_score(document, question)
        candidates.append((source_score + content_score * 0.65, document))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best = candidates[0]
    # An explicit or very close filename always wins. Without one, only use a
    # unique table with a recognisable header/value match; this prevents a
    # generic question from accidentally reading an unrelated module file.
    explicit_score = _source_match_score(best.path, question)
    if explicit_score >= 0.72:
        return best
    if len(candidates) == 1 and (best_score >= 0.55 or _is_structured_query(question)):
        return best
    if best_score >= 0.80 and best_score > candidates[1][0] + 0.18:
        return best
    return None


def _is_structured_query(question: str) -> bool:
    query = normalize(question)
    return any(marker in query for marker in COUNT_MARKERS + SUMMARY_MARKERS) or any(
        marker in query
        for marker in ("coluna", "campo", "nivel de risco", "status", "registros", "linhas", "planilha")
    )


def _find_filter(document: StructuredDocument, question: str) -> tuple[str, str] | None:
    query = normalize(question)
    candidates: list[tuple[int, str, str]] = []
    for header in document.headers:
        header_norm = normalize(header).strip()
        header_in_query = _contains_phrase(query, header_norm) or _compact(header_norm) in _compact(query)
        values = Counter(
            normalize(row.get(header, "")).strip()
            for row in document.rows
            if normalize(row.get(header, "")).strip() and normalize(row.get(header, "")).strip() not in {"-", "n/a", "na"}
        )
        for value_norm in values:
            if _contains_phrase(query, value_norm):
                # Explicitly named columns are stronger than a bare value;
                # longer values avoid selecting “em” before “em risco”.
                score = (100 if header_in_query else 0) + len(value_norm)
                candidates.append((score, header, value_norm))
    if not candidates:
        return None
    _, header, value_norm = max(candidates, key=lambda item: item[0])
    display_value = next(
        (row.get(header, "").strip() for row in document.rows if normalize(row.get(header, "")).strip() == value_norm),
        value_norm,
    )
    return header, display_value


def _record_label(question: str) -> str:
    query = normalize(question)
    if "usuario" in query or "pessoa" in query or "funcionario" in query:
        return "usuários"
    if "documento" in query:
        return "documentos"
    if "item" in query:
        return "itens"
    return "registros"


def _format_answer(
    document: StructuredDocument,
    question: str,
    language: str,
    response_style: str,
    matched_count: int,
    filter_column: str | None,
    filter_value: str | None,
) -> str:
    label = _record_label(question)
    source = document.path.name
    total = len(document.rows)
    if language == "en":
        conclusion = f"There are {matched_count} {label} matching the requested criterion in {source}, out of {total} records."
        basis = f"- Complete read of the table: {total} data rows."
        if filter_column and filter_value:
            basis += f"\n- Criterion: column “{filter_column}” equal to “{filter_value}”."
        attention = "- The count uses only the identified column and value; it does not infer other status fields."
        limits = "- Names, emails and identifiers were not returned; only the aggregate was used."
        if response_style == "concise":
            return f"{conclusion}\n\nSource: {source}. {basis.lstrip('- ')}"
        return f"Conclusion\n{conclusion}\n\nDocumentary basis\n{basis}\n\nPoints of attention\n{attention}\n\nLimits\n{limits}"
    if language == "es":
        conclusion = f"Hay {matched_count} {label} que cumplen el criterio solicitado en {source}, de un total de {total} registros."
        basis = f"- Lectura completa de la tabla: {total} filas de datos."
        if filter_column and filter_value:
            basis += f"\n- Criterio: columna “{filter_column}” igual a “{filter_value}”."
        attention = "- El conteo usa solo la columna y el valor identificados; no infiere otros campos de estado."
        limits = "- No se devolvieron nombres, correos ni identificadores; solo se utilizó el agregado."
        if response_style == "concise":
            return f"{conclusion}\n\nFuente: {source}. {basis.lstrip('- ')}"
        return f"Conclusión\n{conclusion}\n\nBase documental\n{basis}\n\nPuntos de atención\n{attention}\n\nLímites\n{limits}"
    conclusion = f"Há {matched_count} {label} que atendem ao critério solicitado no arquivo {source}, de um total de {total} registros."
    basis = f"- Leitura integral da tabela: {total} linhas de dados."
    if filter_column and filter_value:
        basis += f"\n- Critério aplicado: coluna “{filter_column}” igual a “{filter_value}”."
    attention = "- A contagem usa somente a coluna e o valor identificados; não infere outros campos de estado."
    limits = "- Nomes, e-mails e identificadores não foram retornados; foi utilizado apenas o resultado agregado."
    if response_style == "concise":
        return f"{conclusion}\n\nFonte: {source}. {basis.lstrip('- ')}"
    return f"Conclusão\n{conclusion}\n\nBase documental\n{basis}\n\nPontos de atenção\n{attention}\n\nLimites\n{limits}"


def analyze_structured_question(
    root: Path,
    module_id: str,
    question: str,
    language: str = "pt-BR",
    response_style: str = "structured",
) -> StructuredAnswer | None:
    """Answer supported table counts from the complete source, never a chunk."""
    if not _is_structured_query(question):
        return None
    document = resolve_structured_source(root, module_id, question)
    if document is None:
        return None
    normalized_question = normalize(question)
    filter_spec = _find_filter(document, question)
    if filter_spec:
        filter_column, filter_value = filter_spec
        value_norm = normalize(filter_value).strip()
        matched_count = sum(
            normalize(row.get(filter_column, "")).strip() == value_norm
            for row in document.rows
        )
    else:
        filter_column = filter_value = None
        matched_count = len(document.rows)
    operation = "count_filtered" if filter_spec else "count_rows"
    # A source mention plus “resumo” is still useful even without a filter;
    # the same exact table count is safer than handing a partial chunk to an
    # LLM.  Detailed column profiling can be added without changing this API.
    if not any(marker in normalized_question for marker in COUNT_MARKERS + SUMMARY_MARKERS):
        return None
    return StructuredAnswer(
        _format_answer(document, question, language, response_style, matched_count, filter_column, filter_value),
        document.path,
        len(document.rows),
        matched_count,
        operation,
        filter_column,
        filter_value,
    )
