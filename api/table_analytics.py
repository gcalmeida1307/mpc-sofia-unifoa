"""Typed, deterministic table queries; no eval/SQL supplied by a language model."""
from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from .query_analysis import normalize


def number(value: str) -> Decimal | None:
    value = re.sub(r"(?:R\$|\s)", "", str(value)).strip()
    if not value or value in {"-", "N/A"}:
        return None
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value):
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def infer_schema(document) -> dict[str, dict[str, Any]]:
    schema = {}
    for header in document.headers:
        values = [row.get(header, "") for row in document.rows]
        present = [value for value in values if value.strip() and value not in {"-", "N/A"}]
        numeric = [number(value) for value in present]
        kind = "string"
        if present and all(value is not None for value in numeric) and not any(re.fullmatch(r"0\d+", v) for v in present):
            kind = "integer" if all(value == value.to_integral() for value in numeric) else "decimal"
        elif present and all(normalize(value) in {"true", "false", "sim", "nao"} for value in present):
            kind = "boolean"
        elif present and all(re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T.*)?|\d{2}/\d{2}/\d{4}", value) for value in present):
            kind = "date"
        schema[header] = {"type": kind, "nullable": len(present) != len(values), "null_count": len(values) - len(present), "valid_count": len(present)}
    return schema


def analytical_answer(document, question: str):
    from .structured_data import StructuredAnswer, _contains_phrase
    query = normalize(question)
    operation = next((op for markers, op in [(('correlacao',), 'correlation'), (('soma', 'somatorio', 'valor total'), 'sum'), (('media',), 'average'), (('maior valor', 'maximo'), 'max'), (('menor valor', 'minimo'), 'min')] if any(m in query for m in markers)), None)
    if operation is None:
        return None
    schema = document.schema
    numeric_headers = [h for h in document.headers if schema[h]["type"] in {"integer", "decimal"} and _contains_phrase(query, h)]
    expected = 2 if operation == "correlation" else 1
    if len(numeric_headers) != expected:
        return StructuredAnswer("Preciso identificar " + ("duas colunas numéricas" if expected == 2 else "uma coluna numérica") + f" em {document.path.name}. Colunas disponíveis: {', '.join(document.headers)}.", document.path, len(document.rows), None, "clarification", analysis={"schema": schema, "verified": False})
    filters = []
    for h in document.headers:
        if h in numeric_headers:
            continue
        matches = {row.get(h, "") for row in document.rows if row.get(h, "") and _contains_phrase(query, row[h])}
        if len(matches) == 1:
            filters.append((h, next(iter(matches))))
    sheets = {loc.get("sheet") for loc in document.locations if loc.get("sheet")}
    chosen = [sheet for sheet in sheets if _contains_phrase(query, sheet)]
    rows = [(i, row) for i, row in enumerate(document.rows) if all(normalize(row.get(h, "")) == normalize(v) for h, v in filters) and (not chosen or document.locations[i].get("sheet") in chosen)]
    header = numeric_headers[0]
    group = next((h for h in document.headers if _contains_phrase(query, "por " + h)), None)
    groups = defaultdict(list)
    for i, row in rows:
        groups[row.get(group, "sem valor") if group else "resultado"].append((i, row))
    results = {}
    null_count = 0
    for key, entries in groups.items():
        if operation == "correlation":
            import math
            pairs = [(number(r.get(header, "")), number(r.get(numeric_headers[1], ""))) for _, r in entries]
            pairs = [(float(a), float(b)) for a, b in pairs if a is not None and b is not None]
            if len(pairs) < 3:
                results[key] = None; continue
            ax, ay = (sum(pair[j] for pair in pairs) / len(pairs) for j in (0, 1))
            denominator = math.sqrt(sum((x-ax)**2 for x, y in pairs) * sum((y-ay)**2 for x, y in pairs))
            results[key] = round(sum((x-ax)*(y-ay) for x, y in pairs) / denominator, 6) if denominator else None
        else:
            values = [number(row.get(header, "")) for _, row in entries]
            null_count += sum(value is None for value in values)
            values = [value for value in values if value is not None]
            aggregate = None if not values else {"sum": lambda: sum(values), "average": lambda: sum(values)/len(values), "min": lambda: min(values), "max": lambda: max(values)}[operation]()
            results[key] = str(aggregate) if aggregate is not None else None
    label = {"sum":"A soma", "average":"A média", "min":"O mínimo", "max":"O máximo", "correlation":"A correlação de Pearson"}[operation]
    values_text = "; ".join(f"{key}: {value if value is not None else 'dados insuficientes'}" for key, value in results.items()) or "nenhum registro atende ao filtro"
    answer = f"{label} de {' e '.join(numeric_headers)} em {document.path.name} é {values_text}."
    answer += f"\n\nForam considerados {len(rows)} de {len(document.rows)} registros"
    if filters:
        answer += ", com " + ", ".join(f"{h} = {v}" for h, v in filters)
    if chosen:
        answer += ", na aba " + ", ".join(chosen)
    answer += f". Valores ausentes foram excluídos do cálculo ({null_count})."
    if operation == "correlation":
        answer += " A correlação descreve uma associação nos dados; não demonstra causalidade. São necessárias pelo menos três observações pareadas e variância nas duas colunas."
    answer += f"\n\nFonte: {document.path.name}; colunas: {', '.join(numeric_headers)}."
    return StructuredAnswer(answer, document.path, len(document.rows), len(rows), operation, analysis={"schema": schema, "aggregate": results, "columns": numeric_headers, "filters": filters, "sheets": chosen or sorted(sheets), "nulls_excluded": null_count, "evidence_kind": "correlation" if operation == "correlation" else "fact"})
