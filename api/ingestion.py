from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from contextvars import ContextVar
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
        if payload.get("version") == "formats-2" and payload.get("mtime_ns") == stat.st_mtime_ns and payload.get("size") == stat.st_size:
            return normalize_document_text(path, str(payload.get("text", "")))
    except (OSError, ValueError, TypeError):
        return None
    return None


def _save_cached_text(path: Path, text: str) -> None:
    try:
        stat = path.stat()
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        _cache_path(path).write_text(json.dumps({"version": "formats-2", "mtime_ns": stat.st_mtime_ns, "size": stat.st_size, "text": text}, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        logger.debug("Could not cache %s: %s", path, exc)


def clean_extracted_text(text: str) -> str:
    """Repair PDF line-wrap hyphenation without changing real compound words."""
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


def _noise_key(value: str) -> str:
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(char)
    )
    return " ".join(without_accents.replace("_", " ").split())


def clean_web_capture(text: str) -> str:
    """Remove browser chrome from offline web snapshots before chunking."""
    lines: list[str] = []
    seen: set[str] = set()
    skip_number_after_accessibility = False
    for raw_line in text.replace("\r\n", "\n").split("\n"):
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
        if key in seen:
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
        from .document_pages import extract_pages, read_native_pages, read_pages, pages_ready
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
            from docx.text.paragraph import Paragraph
            from docx.table import Table
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
            if re.search(r"<!\s*(?:DOCTYPE|ENTITY)", raw, re.I):
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


def _paragraphs(text: str) -> list[str]:
    return [" ".join(part.split()) for part in text.replace("\r\n", "\n").split("\n\n") if part.strip()]


def ingest_module(root: Path, module_id: str, max_chars: int = 1800, overlap: int = 250, selected_paths: tuple[Path, ...] | None = None) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    source_paths = selected_paths if selected_paths is not None else tuple(files_for(root, module_id))
    for path in source_paths:
        if path.suffix.lower() == ".pdf" or path.suffix.lower() in IMAGE_EXTENSIONS:
            from .document_pages import extract_pages, read_native_pages, read_pages, pages_ready
            pages = extract_pages(path) if ALLOW_HEAVY_EXTRACTION.get() else read_pages(path)
            if not ALLOW_HEAVY_EXTRACTION.get() and path.suffix.lower() == ".pdf" and (pages is None or not pages_ready(pages)):
                native_pages = read_native_pages(path)
                if native_pages is not None:
                    pages = native_pages
            if not pages or not pages_ready(pages):
                continue
            ordinal = 0
            for page in pages:
                if page.status != "READY":
                    continue
                for start in range(0, len(page.text), max(1, max_chars - overlap)):
                    text = page.text[start:start + max_chars].strip()
                    if text:
                        chunks.append(DocumentChunk(path, text, ordinal, page.number, f"página {page.number}"))
                        ordinal += 1
                    if start + max_chars >= len(page.text):
                        break
            continue
        text = extract_text(path)
        if not text.strip():
            continue
        # Preserva linhas de tabelas e parágrafos; só divide por tamanho quando necessário.
        if path.suffix.lower() == ".csv":
            units = [line.strip() for line in text.splitlines() if line.strip()]
        else:
            units = _paragraphs(text) or [line.strip() for line in text.splitlines() if line.strip()]
        current = ""
        ordinal = 0
        for unit in units:
            if len(current) + len(unit) + 1 <= max_chars:
                current = f"{current}\n{unit}".strip()
                continue
            if current:
                chunks.append(DocumentChunk(path, current, ordinal))
                ordinal += 1
            current = ""
            # A single HTML paragraph or PDF table can be much larger than
            # max_chars. Never carry that whole unit into the next chunk.
            step = max(1, max_chars - overlap)
            start = 0
            while len(unit) - start > max_chars:
                chunks.append(DocumentChunk(path, unit[start:start + max_chars], ordinal))
                ordinal += 1
                start += step
            current = unit[start:]
        if current:
            chunks.append(DocumentChunk(path, current, ordinal))
    return chunks
