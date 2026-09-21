from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import shutil
import sqlite3
import unicodedata
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from openpyxl import load_workbook
from pypdf import PdfReader

try:
    import pymupdf as fitz
except ImportError:  # PyMuPDF is optional; pypdf remains the compatibility fallback.
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:  # OCR remains optional for environments without the native engine.
    Image = None
    pytesseract = None

logger = logging.getLogger("sofia.ingestion")
ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = ROOT / "data" / "text-cache"
ALLOW_HEAVY_EXTRACTION: ContextVar[bool] = ContextVar("allow_heavy_extraction", default=True)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".log", ".pdf", ".docx", ".xlsx"}
ALLOWED_EXTENSIONS = TEXT_EXTENSIONS | IMAGE_EXTENSIONS
_TESSERACT_PATH = shutil.which("tesseract")
if not _TESSERACT_PATH:
    for candidate in (r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
        if Path(candidate).exists():
            _TESSERACT_PATH = candidate
            break
if pytesseract is not None and _TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_PATH


@dataclass(frozen=True)
class DocumentChunk:
    path: Path
    text: str
    ordinal: int
    page: int | None = None
    locator: str = ""
    start_line: int | None = None
    end_line: int | None = None
    section_header: str = ""
    content_type: str = "prose"
    quality_score: float = 1.0


def ocr_status() -> dict[str, str | bool]:
    """Report whether image text extraction is ready on this machine."""
    return {
        "available": bool(Image is not None and pytesseract is not None and _TESSERACT_PATH),
        "engine": "tesseract" if _TESSERACT_PATH else "not-installed",
        "language": os.getenv("SOFIA_OCR_LANG", "por+eng"),
    }


def files_for(root: Path, module_id: str) -> list[Path]:
    module_root = root / module_id
    return sorted(
        p
        for p in module_root.rglob("*")
        if p.is_file()
        and p.name != ".gitkeep"
        and p.suffix.lower() in ALLOWED_EXTENSIONS
        and not {part.casefold() for part in p.relative_to(module_root).parts} & {"quarantine", ".versions"}
    )


def ready_files_for(root: Path, module_id: str) -> list[Path]:
    """Return only sources approved by the persistent document pipeline.

    Legacy/test workspaces without a pipeline database keep the previous
    behaviour so isolated retrieval tests and first-run development remain
    usable. Once the database exists and has records for a module, unknown
    physical files are excluded until they reach ``READY``.
    """

    paths = files_for(root, module_id)
    database = root.parent / "data" / "knowledge_expansion.sqlite3"
    if not database.exists():
        return paths
    try:
        connection = sqlite3.connect(database, timeout=2)
        rows = connection.execute(
            "SELECT path, status, validation_status FROM documents WHERE module_id = ?",
            (module_id,),
        ).fetchall()
        connection.close()
    except sqlite3.Error:
        logger.warning("Não foi possível consultar o estado do corpus de %s", module_id, exc_info=True)
        return []
    if not rows:
        return paths
    status_by_path = {
        str(Path(str(path)).resolve()).casefold(): (str(status).upper(), str(validation or "").upper())
        for path, status, validation in rows
    }
    return [
        path
        for path in paths
        if status_by_path.get(str(path.resolve()).casefold()) in {("READY", "READY"), ("READY", "")}
    ]


def _read_text_file(path: Path) -> str:
    """Read user documents without corrupting UTF-8 or legacy Windows text."""
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _cache_path(path: Path) -> Path:
    digest = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:32]
    return CACHE_ROOT / f"{digest}.json"


def _cached_text(path: Path) -> str | None:
    cache = _cache_path(path)
    try:
        payload = json.loads(cache.read_text(encoding="utf-8"))
        stat = path.stat()
        if payload.get("version") == "formats-6" and payload.get("mtime_ns") == stat.st_mtime_ns and payload.get("size") == stat.st_size:
            return normalize_document_text(path, str(payload.get("text", "")))
    except (OSError, ValueError, TypeError):
        return None
    return None


def _save_cached_text(path: Path, text: str) -> None:
    try:
        stat = path.stat()
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        _cache_path(path).write_text(json.dumps({"version": "formats-6", "mtime_ns": stat.st_mtime_ns, "size": stat.st_size, "text": text}, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        logger.debug("Could not cache %s: %s", path, exc)


def clean_extracted_text(text: str) -> str:
    """Repair PDF line-wrap hyphenation without changing real compound words."""
    # Several PDF text maps use typographic spaces (U+2004/U+2005, NBSP and
    # narrow NBSP) between ``Art.`` and its number.  Python's ``\s`` does not
    # match every one of those glyphs, so structural retrieval could not see
    # anchors such as ``Art. 59`` even though they were visibly present.
    text = re.sub(r"[\u00a0\u2000-\u200b\u202f]", " ", str(text or ""))
    text = text.replace("\u00ad", "")
    text = re.sub(r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ])-\s*\n\s*(?=[a-zà-öø-ÿ])", "", text)
    # Some PDF extractors preserve a line-break hyphen as ``cita-ção`` after
    # flattening the line. Repair common Portuguese suffixes while keeping
    # ordinary compounds such as “guarda-chuva” intact.
    return re.sub(
        r"(?i)\b([a-zà-öø-ÿ]{3,})-(?=(?:ção|ções|são|sões|mento|mente|dade|dades|tivo|tiva|tivos|tivas)\b)",
        r"\1",
        text,
    )


WEB_CAPTURE_NOISE = {
    "menu",
    "buscar",
    "busca no site",
    "buscar cursos",
    "filtrar",
    "filtrado por:",
    "pt",
    "en",
    "es",
    "entrar",
    "home",
    "x",
    "info",
    "schedule",
    "chevron right",
    "chevron left",
    "expand less",
    "rolar para esquerda",
    "rolar para direita",
    "ajuda",
    "botao menu",
    "assuntos",
    "acessibilidade",
    "alto contraste",
    "ferramentas pessoais",
    "temas",
    "comunicados em destaque",
    "pesquisar",
    "resultados da pesquisa",
    "carregando",
    "servicos relacionados",
    "mais informacoes",
    "fale conosco",
    "compartilhe",
    "redefinir cookies",
    "links de compartilhamento em redes sociais",
    "voltar ao topo da pagina",
    "rejeitar",
    "fale agora",
    "refazer a busca",
}

# A web capture repeats navigation labels, but repeated content labels carry
# the value of each course/program and must not be globally de-duplicated.
# Dropping the second ``Carga Horária`` was the reason the ENAP course lost its
# 20h value even though the raw file contained it.
WEB_CAPTURE_REPEATABLE_CONTENT = {
    "carga horaria",
    "conteudista",
    "certificador",
    "lancamento",
    "oferta",
    "disponibilidade",
    "idioma",
    "publico alvo",
    "criterios para obtencao do certificado",
}


def _noise_key(value: str) -> str:
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(char)
    )
    return " ".join(without_accents.replace("_", " ").split())


def clean_web_capture(text: str) -> str:
    """Remove browser chrome from offline web snapshots before chunking."""
    raw_lines = text.replace("\r\n", "\n").split("\n")
    header = raw_lines[:4] if raw_lines and raw_lines[0].lstrip().startswith("#") else []
    body = raw_lines[len(header):]

    # Institutional crawls may contain several pages in one snapshot. Each
    # page repeats the full menu, then a breadcrumb and an ``Info`` marker.
    # Extract every article segment independently; cutting the whole body at
    # the first repeated menu would silently lose later pages (including the
    # law passage that the user explicitly needs).
    breadcrumbs = [index for index, line in enumerate(body) if _noise_key(line).rstrip(":") == "voce esta aqui"]
    if breadcrumbs:
        articles: list[str] = []
        for position, breadcrumb in enumerate(breadcrumbs):
            boundary = breadcrumbs[position + 1] if position + 1 < len(breadcrumbs) else len(body)
            info = next((index for index in range(breadcrumb + 1, boundary) if _noise_key(body[index]) == "info"), None)
            if info is None:
                continue
            segment = body[max(breadcrumb, info - 2):boundary]
            segment_keys = [_noise_key(line) for line in segment]
            cut = next(
                (index for index in range(5, max(5, len(segment_keys) - 2)) if segment_keys[index:index + 3] == ["acesso a informacao", "institucional", "estrutura organizacional"]),
                len(segment),
            )
            articles.extend(segment[:cut])
            articles.append("")
        if articles:
            body = articles

    lines: list[str] = []
    seen: set[str] = set()
    skip_number_after_accessibility = False
    for raw_line in [*header, *body]:
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        key = _noise_key(line)
        # gov.br appends a large, unrelated national services footer to many
        # pages. It is not part of the captured module knowledge.
        if (key in {"servicos e informacoes do brasil", "servicos para voce"} or line.casefold().startswith("## gov.br")) and lines:
            break
        if key.startswith(("fonte:", "url:", "capturado em:", "paginas no dominio:")):
            continue
        if key.startswith(("ir para ", "abrir menu principal", "termos mais buscados")):
            skip_number_after_accessibility = True
            continue
        if skip_number_after_accessibility and re.fullmatch(r"\d+", key):
            skip_number_after_accessibility = False
            continue
        skip_number_after_accessibility = False
        if key in WEB_CAPTURE_NOISE or key in {"chevron_right", "chevron_left", "expand_less"}:
            continue
        if key in seen and key not in WEB_CAPTURE_REPEATABLE_CONTENT:
            continue
        seen.add(key)
        lines.append(line)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def normalize_document_text(path: Path, text: str) -> str:
    """Apply the right normalization for the source format."""
    text = clean_extracted_text(text)
    if path.suffix.lower() == ".md" and (
        path.parent.name.casefold() == "links"
        or re.search(r"^(?:Fonte|URL|Capturado em|Páginas no domínio):", text, re.MULTILINE | re.IGNORECASE)
    ):
        return clean_web_capture(text)
    return text


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf" or path.suffix.lower() in IMAGE_EXTENSIONS:
        from .document_pages import (
            extract_pages,
            pages_ready,
            read_native_pages,
            read_pages,
        )
        pages = extract_pages(path) if ALLOW_HEAVY_EXTRACTION.get() else read_pages(path)
        # Native PDF text is cheap and does not violate the no-heavy-work
        # query contract.  It keeps older, encrypted page caches usable while
        # still refusing scanned pages until the OCR preparation pipeline runs.
        if not ALLOW_HEAVY_EXTRACTION.get() and path.suffix.lower() == ".pdf" and (pages is None or not pages_ready(pages)):
            native_pages = read_native_pages(path)
            if native_pages is not None:
                pages = native_pages
        if not pages or not pages_ready(pages):
            return ""
        return "\n\n".join(f"[Página {p.number}]\n{p.text}" for p in pages if p.status == "READY")
    cached = _cached_text(path)
    if cached is not None:
        cached = normalize_document_text(path, cached)
        # PDFs digitalizados podem ter sido cacheados apenas com quebras de
        # linha pela extração textual. Quando o OCR está disponível, refaça a
        # leitura para que o cache não congele um documento inutilizável.
        if not (path.suffix.lower() == ".pdf" and len(cached.strip()) < 80 and Image is not None and pytesseract is not None and _TESSERACT_PATH):
            return cached
    try:
        suffix = path.suffix.lower()
        if not ALLOW_HEAVY_EXTRACTION.get() and suffix in {".docx", ".xlsx"}:
            return ""
        if suffix == ".pdf":
            if fitz is not None:
                with fitz.open(str(path)) as document:
                    text = "\n".join(page.get_text("text") for page in document)
                    if len(text.strip()) < 80 and Image is not None and pytesseract is not None and _TESSERACT_PATH:
                        # Alguns acordos e regulamentos são PDFs formados por
                        # imagens. Renderizar somente nesse caso mantém PDFs
                        # textuais rápidos e torna o documento consultável.
                        ocr_pages: list[str] = []
                        for page in document:
                            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                            with Image.open(io.BytesIO(pixmap.tobytes("png"))) as image:
                                ocr_pages.append(pytesseract.image_to_string(image, lang=os.getenv("SOFIA_OCR_LANG", "por+eng"), config="--psm 6"))
                        text = "\n".join(ocr_pages)
            else:
                text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        elif suffix == ".docx":
            # Preserve paragraph/table order and label cells with their header.
            document = Document(str(path))
            from docx.table import Table
            from docx.text.paragraph import Paragraph
            blocks = []
            for child in document.element.body:
                if child.tag.endswith("}p"):
                    blocks.append(Paragraph(child, document).text)
                elif child.tag.endswith("}tbl"):
                    rows = Table(child, document).rows
                    if rows:
                        headers = [cell.text for cell in rows[0].cells]
                        blocks.extend("; ".join(f"{headers[i]}: {cell.text}" for i, cell in enumerate(row.cells)) for row in rows[1:])
            text = "\n\n".join(blocks)
        elif suffix == ".xml":
            import xml.etree.ElementTree as ET
            raw = _read_text_file(path)
            if re.search(r"<!\s*(?:DOCTYPE|ENTITY)", raw, re.IGNORECASE):
                raise ValueError("XML DTD/entities não permitidas")
            node = ET.fromstring(raw)
            def xml_lines(element, parent=""):
                tag = element.tag.split("}")[-1]
                location = f"{parent}/{tag}"
                lines = [f"{location}/@{key}: {value}" for key, value in element.attrib.items()]
                if element.text and element.text.strip():
                    lines.append(f"{location}: {element.text.strip()}")
                for child in element:
                    lines.extend(xml_lines(child, location))
                return lines
            text = "\n".join(xml_lines(node))
        elif suffix == ".xlsx":
            workbook = load_workbook(path, read_only=True, data_only=True)
            rows = []
            for sheet in workbook.worksheets:
                rows.append(f"[PLANILHA: {sheet.title}]")
                rows.extend(" | ".join(str(value) for value in row if value is not None) for row in sheet.iter_rows(values_only=True))
            workbook.close()
            text = "\n".join(row for row in rows if row.strip())
        elif suffix in IMAGE_EXTENSIONS:
            if Image is None or pytesseract is None or not _TESSERACT_PATH:
                logger.warning("OCR indisponível para %s", path)
                return ""
            with Image.open(path) as image:
                text = pytesseract.image_to_string(image, lang=os.getenv("SOFIA_OCR_LANG", "por+eng"), config="--psm 6")
        elif suffix == ".csv":
            rows = csv.reader(io.StringIO(_read_text_file(path)))
            text = "\n".join(" | ".join(row) for row in rows)
        else:
            text = _read_text_file(path)
        text = normalize_document_text(path, text)
        _save_cached_text(path, text)
        return text
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read %s: %s", path, exc)
        return ""


def read_exact_source_lines(path: Path, start: int, end: int) -> str:
    """Read an explicit line range without passing through chunk ranking.

    Text-like sources retain their original file line numbers.  For binary
    formats there is no stable source-line concept, so the prepared extracted
    representation is used as the documented fallback.  This function is
    intentionally bounded to the requested range and never performs OCR when
    called by the question path.
    """

    if start < 1 or end < start:
        return ""
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".log"}:
        raw = _read_text_file(path)
    else:
        raw = extract_text(path)
    lines = raw.replace("\r\n", "\n").splitlines()
    if start > len(lines):
        return ""
    return "\n".join(lines[start - 1 : min(end, len(lines))]).strip()


def read_exact_source_term(path: Path, term: str, limit: int = 8) -> list[tuple[int, str]]:
    """Find literal occurrences and return their real source line numbers."""

    needle = " ".join(str(term or "").split()).strip()
    if not needle:
        return []
    try:
        raw = _read_text_file(path) if path.suffix.lower() in {".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".log"} else extract_text(path)
    except (OSError, RuntimeError, ValueError):
        return []
    def fold(value: str) -> str:
        return "".join(
            char
            for char in unicodedata.normalize("NFKD", value.casefold())
            if not unicodedata.combining(char)
        )

    normalized_needle = " ".join(fold(needle).split())
    matches: list[tuple[int, str]] = []
    for line_number, line in enumerate(raw.replace("\r\n", "\n").splitlines(), start=1):
        normalized_line = " ".join(fold(line).split())
        if normalized_needle and normalized_needle in normalized_line:
            matches.append((line_number, line.strip()))
            if len(matches) >= limit:
                break
    return matches


def _paragraphs(text: str) -> list[str]:
    return [" ".join(part.split()) for part in text.replace("\r\n", "\n").split("\n\n") if part.strip()]


_STRUCTURAL_BOUNDARY = re.compile(
    r"(?i)^(?:"
    r"#{1,6}\s+|"
    r"(?:t[ií]tulo|cap[ií]tulo|se[cç][aã]o|subse[cç][aã]o|cl[aá]usula)\b|"
    r"(?:art(?:igo)?\.?\s*\d+[A-Za-zºª-]*\b)|"
    r"(?:par[aá]grafo\s+[uú]nico\b)|"
    r"(?:§\s*\d+)"
    r")"
)


def _is_structural_boundary(line: str) -> bool:
    return bool(_STRUCTURAL_BOUNDARY.match(line.strip()))


def _text_units(text: str, suffix: str) -> list[tuple[str, int, int]]:
    """Build text units and preserve line provenance for answer citations."""
    lines = text.replace("\r\n", "\n").splitlines()
    if suffix == ".csv":
        return [(line.strip(), index, index) for index, line in enumerate(lines, start=1) if line.strip()]
    units: list[tuple[str, int, int]] = []
    current: list[str] = []
    start = 0
    for index, line in enumerate(lines, start=1):
        # Keep legal articles, clauses and titled sections as independent
        # semantic units even when the extractor removed blank lines.  Size
        # based chunking remains the bounded fallback for unusually large
        # units, but it no longer decides the document hierarchy by itself.
        if current and _is_structural_boundary(line):
            units.append((" ".join(current), start, index - 1))
            current = []
        if line.strip():
            if not current:
                start = index
            current.append(line.strip())
            continue
        if current:
            # A heading followed by a blank line still belongs to the
            # structural unit that follows it.  Keeping the heading open
            # here lets the ingestion layer attach ``Origem``/``Art. 5``/
            # ``Cláusula 3`` to its first paragraph instead of indexing the
            # heading as an orphaned chunk.
            if len(current) == 1 and _is_structural_boundary(current[0]):
                continue
            units.append((" ".join(current), start, index - 1))
            current = []
    if current:
        units.append((" ".join(current), start, len(lines)))
    return units or [(line.strip(), index, index) for index, line in enumerate(lines, start=1) if line.strip()]


def _section_header(text: str, line_start: int) -> str:
    lines = text.replace("\r\n", "\n").splitlines()
    if not lines:
        return ""
    for line in reversed(lines[: max(0, line_start)]):
        value = line.strip()
        if re.match(r"^#{1,6}\s+", value) or value.startswith("[PLANILHA:") or _is_structural_boundary(value):
            return re.sub(r"^#{1,6}\s+", "", value).strip()[:240]
    return ""


def _content_type(path: Path, text: str) -> str:
    suffix = path.suffix.casefold()
    if suffix in {".csv", ".xlsx", ".json"}:
        return "structured_data"
    if suffix == ".xml":
        return "xml_record"
    if suffix in IMAGE_EXTENSIONS:
        return "ocr_image"
    if suffix == ".pdf":
        return "ocr_pdf" if len(re.findall(r"\[Página\s+\d+\]", text)) else "pdf_text"
    normalized = normalize_document_text(path, text)
    if path.parent.name.casefold() == "links" and any(marker in normalized.casefold() for marker in ("cursos relacionados", "cursos do programa", "carga horária")):
        return "list_catalog"
    if path.suffix.casefold() in {".md", ".txt", ".log"} and sum(1 for line in text.splitlines() if line.strip()) >= 20:
        return "text_document"
    return "prose"


_CONTINUATION_ENDINGS = {
    "a", "ao", "aos", "as", "com", "da", "das", "de", "do", "dos", "e", "em",
    "na", "nas", "no", "nos", "o", "os", "ou", "para", "pela", "pelas", "pelo",
    "pelos", "por", "que", "se", "um", "uma", "uns", "umas",
}


def _needs_pdf_continuation(text: str) -> bool:
    """Identify a page chunk that visibly ends before its sentence."""

    compact = " ".join(str(text or "").split()).strip()
    if not compact:
        return False
    if compact.endswith(","):
        return True
    if re.search(r"[.!?;:]\s*[\"'»)]?$", compact):
        return False
    last_word = re.findall(r"[\wÀ-ÿ]+", compact.casefold())
    if last_word and last_word[-1] in _CONTINUATION_ENDINGS:
        return True
    # Fixed-size PDF chunks can also split a word (``infer`` + ``ior``) or
    # end after a complete word while the sentence continues on the next
    # chunk. A non-punctuated alphabetic ending is strong enough evidence for
    # a bounded continuation view; ordinary completed sentences were already
    # returned above.
    return bool(re.search(r"[\wÀ-ÿ)]$", compact))


def _stitch_pdf_continuations(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    """Add a bounded cross-page view without changing page provenance.

    Legal and technical PDFs frequently split an article at the physical page
    boundary.  A page-only index then retrieves a passage ending in ``o`` or
    ``de`` and the answer composer can only reproduce an incomplete sentence.
    The original pages remain available; an incomplete chunk gets a bounded
    view with only the next textual continuation.  Headings and new articles
    are never pulled into that view.
    """

    result = list(chunks)
    by_source: dict[Path, list[DocumentChunk]] = {}
    for chunk in chunks:
        if chunk.page is not None:
            by_source.setdefault(chunk.path, []).append(chunk)
    replacements: dict[tuple[Path, int], DocumentChunk] = {}

    def merge_overlap(left: str, right: str) -> str | None:
        """Merge adjacent overlapping chunks without repeating their overlap."""
        maximum = min(400, len(left), len(right))
        for size in range(maximum, 39, -1):
            if left[-size:] == right[:size]:
                return left + right[size:]
        return None

    for path, source_chunks in by_source.items():
        ordered = sorted(source_chunks, key=lambda chunk: chunk.ordinal)
        for index, current in enumerate(ordered):
            if not _needs_pdf_continuation(current.text):
                continue
            combined = current.text.rstrip()
            end_page = int(current.page)
            quality = current.quality_score
            next_index = index + 1
            for _ in range(2):
                if not _needs_pdf_continuation(combined):
                    break
                if next_index >= len(ordered):
                    break
                next_first = ordered[next_index]
                # Chunks from the same page overlap by design.  Merge their
                # union, rather than appending the overlap a second time.
                if next_first.page == current.page:
                    merged = merge_overlap(combined, next_first.text)
                    if merged is None:
                        break
                    combined = merged
                    next_index += 1
                    continue
                next_start = " ".join(next_first.text.split()).lstrip()
                # Every printed page of the Vade starts with ``N Consolidação
                # ...``.  It is provenance noise, not the continuation text;
                # remove it before deciding whether the next chunk continues
                # the sentence.
                next_start = re.sub(
                    r"(?i)^\d+\s+consolida[cç][aã]o\s+das\s+leis\s+do\s+trabalho\s*",
                    "",
                    next_start,
                ).lstrip(" -•\t")
                if not next_start or re.match(
                    r"(?i)^(?:cap[ií]tulo|se[cç][aã]o|art(?:igo)?\.?\s*\d|cl[aá]usula)\b",
                    next_start,
                ):
                    break
                # A continuation must begin as ordinary prose (or with a
                # closing punctuation marker).  This prevents a page ending
                # in a navigation/header fragment from swallowing the next
                # article or clause.
                if not re.match(r"(?i)^(?:[a-zà-öø-ÿ]|[§,;:)])", next_start):
                    break
                combined = f"{combined}\n{next_start[:900].rstrip()}"
                if next_first.page is not None:
                    end_page = int(next_first.page)
                quality = min(quality, next_first.quality_score)
                next_index += 1
            if combined == current.text.rstrip():
                continue
            locator = f"página {current.page}" if end_page == current.page else f"páginas {current.page}-{end_page}"
            replacements[(path, current.ordinal)] = DocumentChunk(
                current.path,
                combined,
                current.ordinal,
                current.page,
                locator,
                current.start_line,
                current.end_line,
                current.section_header,
                current.content_type,
                quality,
            )
    if not replacements:
        return result
    return [replacements.get((chunk.path, chunk.ordinal), chunk) for chunk in result]


def ingest_module(root: Path, module_id: str, max_chars: int = 1800, overlap: int = 250, selected_paths: tuple[Path, ...] | None = None) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    source_paths = selected_paths if selected_paths is not None else tuple(files_for(root, module_id))
    for path in source_paths:
        if path.suffix.lower() == ".pdf" or path.suffix.lower() in IMAGE_EXTENSIONS:
            from .document_pages import (
                extract_pages,
                pages_ready,
                read_native_pages,
                read_pages,
            )
            pages = extract_pages(path) if ALLOW_HEAVY_EXTRACTION.get() else read_pages(path)
            if not ALLOW_HEAVY_EXTRACTION.get() and path.suffix.lower() == ".pdf" and (pages is None or not pages_ready(pages)):
                native_pages = read_native_pages(path)
                if native_pages is not None:
                    pages = native_pages
            # A document with one unreadable page must not be advertised as
            # fully ready, but its readable pages remain valid evidence.  The
            # pipeline status still comes from ``pages_ready`` and therefore
            # remains partial/quarantined; retrieval can use only READY pages
            # instead of losing an otherwise usable manual completely.
            if not pages or not any(page.status == "READY" for page in pages):
                continue
            path_chunks: list[DocumentChunk] = []
            ordinal = 0
            for page in pages:
                if page.status != "READY":
                    continue
                page_units = _text_units(page.text, ".txt") or [(page.text, 1, 1)]
                for unit, line_start, line_end in page_units:
                    step = max(1, max_chars - overlap)
                    for start in range(0, len(unit), step):
                        text = unit[start:start + max_chars].strip()
                        if text:
                            path_chunks.append(
                                DocumentChunk(
                                    path,
                                    text,
                                    ordinal,
                                    page.number,
                                    f"página {page.number}",
                                    line_start,
                                    line_end,
                                    _section_header(page.text, line_start),
                                    _content_type(path, f"[Página {page.number}]\n{page.text}" if page.method == "ocr" else page.text),
                                    page.quality,
                                )
                            )
                            ordinal += 1
                        if start + max_chars >= len(unit):
                            break
            chunks.extend(_stitch_pdf_continuations(path_chunks))
            continue
        text = extract_text(path)
        if not text.strip():
            continue
        # Catálogos capturados da web precisam preservar cada item como uma
        # unidade própria.  Se eles forem achatados em um único parágrafo,
        # títulos de cursos, descrições e metadados se misturam e a resposta
        # perde a proveniência por linha.
        content_type = _content_type(path, text)
        if content_type == "list_catalog":
            units = [
                (line.strip(), index, index)
                for index, line in enumerate(text.replace("\r\n", "\n").splitlines(), start=1)
                if line.strip()
            ]
        else:
            # Preserva linhas de tabelas e parágrafos; só divide por tamanho quando necessário.
            units = _text_units(text, path.suffix.lower())
        current = ""
        current_start = 0
        current_end = 0
        ordinal = 0
        for unit, line_start, line_end in units:
            # Do not silently merge independent sections/articles into one
            # large chunk.  A semantic boundary must remain visible in the
            # index and in the evidence package even when the whole document
            # fits below ``max_chars``.
            starts_structural_unit = _is_structural_boundary(unit)
            if current and starts_structural_unit:
                locator = f"linhas {current_start}-{current_end}" if current_start else ""
                chunks.append(
                    DocumentChunk(
                        path,
                        current,
                        ordinal,
                        None,
                        locator,
                        current_start,
                        current_end,
                        _section_header(text, current_start),
                        content_type,
                    )
                )
                ordinal += 1
                current = ""
                current_start = 0
                current_end = 0
            if len(current) + len(unit) + 1 <= max_chars:
                if not current:
                    current_start = line_start
                current_end = line_end
                current = f"{current}\n{unit}".strip()
                continue
            if current:
                locator = f"linhas {current_start}-{current_end}" if current_start else ""
                chunks.append(
                    DocumentChunk(
                        path,
                        current,
                        ordinal,
                        None,
                        locator,
                        current_start,
                        current_end,
                        _section_header(text, current_start),
                        content_type,
                    )
                )
                ordinal += 1
            current = ""
            # A single HTML paragraph or PDF table can be much larger than
            # max_chars. Never carry that whole unit into the next chunk.
            step = max(1, max_chars - overlap)
            start = 0
            while len(unit) - start > max_chars:
                locator = f"linhas {line_start}-{line_end}"
                chunks.append(
                    DocumentChunk(
                        path,
                        unit[start:start + max_chars],
                        ordinal,
                        None,
                        locator,
                        line_start,
                        line_end,
                        _section_header(text, line_start),
                        content_type,
                    )
                )
                ordinal += 1
                start += step
            current = unit[start:]
            current_start = line_start
            current_end = line_end
        if current:
            locator = f"linhas {current_start}-{current_end}" if current_start else ""
            chunks.append(
                DocumentChunk(
                    path,
                    current,
                    ordinal,
                    None,
                    locator,
                    current_start,
                    current_end,
                    _section_header(text, current_start),
                    content_type,
                )
            )
    return chunks
