"""Page-level extraction and quality gate, independent of chat and providers."""
from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from .secure_storage import decrypt_text, protect_for_storage

EXTRACTOR_VERSION = "pages-4"


@dataclass(frozen=True)
class ExtractedPage:
    number: int
    text: str
    method: str
    quality: float
    status: str
    reason: str = ""


def text_quality(text: str) -> float:
    import re
    # PDF text maps sometimes contain backspace/control glyphs between every
    # word. They are extraction artifacts, not evidence that the page is
    # unreadable; score the sanitized text and keep the same sanitization in
    # the page artifact below.
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text).strip()
    words = re.findall(r"[^\W_]+", clean, re.UNICODE)
    if len(words) < 3 or len(clean) < 15:
        return 0.0
    readable = sum(char.isalnum() or char.isspace() or char in ".,;:!?%()/+-'\"ºª°" for char in clean) / len(clean)
    bad = sum(char == "\ufffd" or (ord(char) < 32 and not char.isspace()) for char in clean) / len(clean)
    return round(max(0.0, min(1.0, readable - bad * 4)), 4)


def cache_path(path: Path) -> Path:
    from .ingestion import CACHE_ROOT
    key = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
    return CACHE_ROOT / "pages" / f"{key}.json"


def read_pages(path: Path) -> tuple[ExtractedPage, ...] | None:
    try:
        raw = cache_path(path).read_text(encoding="utf-8")
        try:
            decoded = decrypt_text(raw)
        except RuntimeError:
            decoded = raw if raw.lstrip().startswith("{") else ""
        payload = json.loads(decoded)
        stat = path.stat()
        if payload.get("version") != EXTRACTOR_VERSION or payload.get("mtime") != stat.st_mtime_ns or payload.get("size") != stat.st_size:
            return None
        return tuple(ExtractedPage(**page) for page in payload["pages"])
    except (OSError, ValueError, TypeError, KeyError, RuntimeError):
        return None


def read_native_pages(path: Path) -> tuple[ExtractedPage, ...] | None:
    """Read only the embedded PDF text, without OCR or cache writes.

    This is a compatibility fallback for legacy caches that were encrypted
    before the current process loaded ``SOFIA_ENCRYPTION_KEY``.  It is safe for
    the query path because it never renders pages or invokes Tesseract.  A
    scanned PDF with no meaningful embedded text therefore remains unavailable
    until the preparation pipeline runs with OCR enabled.
    """
    if path.suffix.casefold() != ".pdf":
        return None
    try:
        from .ingestion import clean_extracted_text, fitz
        pages: list[ExtractedPage] = []
        if fitz is not None:
            with fitz.open(path) as document:
                for number, page in enumerate(document, 1):
                    text = clean_extracted_text(page.get_text("text") or "")
                    if not text.strip() and not page.get_images() and not page.get_drawings():
                        pages.append(ExtractedPage(number, "", "blank", 1.0, "BLANK"))
                        continue
                    text = _sanitize_page_text(text)
                    quality = text_quality(text)
                    pages.append(ExtractedPage(number, text, "native", quality, "READY" if quality >= 0.75 else "QUARANTINED", "OCR não executado durante a consulta" if quality < 0.75 else ""))
        else:
            from pypdf import PdfReader
            for number, page in enumerate(PdfReader(path).pages, 1):
                text = clean_extracted_text(page.extract_text() or "")
                text = _sanitize_page_text(text)
                quality = text_quality(text)
                pages.append(ExtractedPage(number, text, "native", quality, "READY" if quality >= 0.75 else "QUARANTINED", "OCR não executado durante a consulta" if quality < 0.75 else ""))
        # For this query-only compatibility path, retain readable native
        # pages even when a long PDF contains an unreadable/scanned page.  The
        # actual preparation pipeline still uses ``extract_pages`` and the
        # strict all-pages quality gate, so this never marks the document ready.
        readable = tuple(page for page in pages if page.status in {"READY", "BLANK"})
        return readable if any(page.status == "READY" for page in readable) else None
    except (OSError, ValueError, TypeError):
        return None


def _ocr(image) -> tuple[str, float]:
    from .ingestion import pytesseract
    data = pytesseract.image_to_data(image, lang=os.getenv("SOFIA_OCR_LANG", "por+eng"), config="--psm 6", output_type=pytesseract.Output.DICT, timeout=45)
    words, confidences, lines = [], [], []
    last_line = None
    for i, word in enumerate(data["text"]):
        if not word.strip():
            continue
        line = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        if last_line is not None and line != last_line:
            lines.append(" ".join(words)); words = []
        last_line = line
        words.append(word)
        confidences.append(max(0.0, float(data["conf"][i])) / 100)
    if words:
        lines.append(" ".join(words))
    return "\n".join(lines), sum(confidences) / max(1, len(confidences))


def _sanitize_page_text(text: str) -> str:
    """Remove non-printing PDF mapping artifacts before indexing or scoring."""
    import re
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text).replace("\ufffd", "")


def extract_pages(path: Path) -> tuple[ExtractedPage, ...]:
    from .ingestion import Image, fitz, ocr_status, clean_extracted_text
    cached = read_pages(path)
    if cached is not None:
        return cached
    pages: list[ExtractedPage] = []

    def process(number: int, native: str, render, blank: bool = False, force_ocr: bool = False, section_marker: bool = False):
        native = _sanitize_page_text(native)
        text, method, quality, reason = native, "native", text_quality(native), ""
        if blank:
            pages.append(ExtractedPage(number, "", "blank", 1.0, "BLANK")); return
        if section_marker:
            # Short native headings such as “Constituição Federal” are
            # meaningful page provenance, but their two or three words are
            # below the generic density score and do not need OCR.
            pages.append(ExtractedPage(number, native, "native", 0.95, "READY", "marcador de seção")); return
        if quality < 0.75 or force_ocr:
            if ocr_status()["available"]:
                try:
                    with render() as image:
                        text, confidence = _ocr(image)
                    method, quality = "ocr", min(text_quality(text), confidence)
                except Exception as exc:
                    text, method, quality, reason = "", "ocr", 0.0, type(exc).__name__
            else:
                reason = "OCR indisponível"
        status = "READY" if quality >= 0.75 else "QUARANTINED"
        pages.append(ExtractedPage(number, clean_extracted_text(text), method, round(quality, 4), status, reason or ("baixa legibilidade" if status != "READY" else "")))

    if path.suffix.lower() == ".pdf":
        if fitz is None:
            from pypdf import PdfReader
            for n, page in enumerate(PdfReader(path).pages, 1):
                text = page.extract_text() or ""
                score = text_quality(text)
                pages.append(ExtractedPage(n, text, "native", score, "READY" if score >= .75 else "QUARANTINED", "renderizador OCR indisponível" if score < .75 else ""))
        else:
            with fitz.open(path) as doc:
                for n, page in enumerate(doc, 1):
                    native = page.get_text("text")
                    # Vector-only divider pages contain no recoverable text;
                    # they should not trigger a fake OCR failure. A scanned
                    # page still has an image and is sent through the strict
                    # OCR gate below.
                    blank = not native.strip() and not page.get_images()
                    image_area = sum(rect.get_area() for info in page.get_images() for rect in page.get_image_rects(info[0]))
                    scanned_body = image_area > page.rect.get_area() * .5 and len(native.strip()) < 40
                    section_marker = bool(native.strip()) and not page.get_images() and len(native.strip()) <= 120 and len(native.split()) <= 12
                    process(n, native, lambda page=page: Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).tobytes("png"))), blank, scanned_body, section_marker)
    else:
        with Image.open(path) as image:
            from PIL import ImageSequence
            for n, frame in enumerate(ImageSequence.Iterator(image), 1):
                process(n, "", lambda frame=frame: frame.convert("RGB"))
    destination = cache_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stat = path.stat()
    payload = {"version": EXTRACTOR_VERSION, "mtime": stat.st_mtime_ns, "size": stat.st_size, "pages": [asdict(p) for p in pages]}
    fd, name = tempfile.mkstemp(dir=destination.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(protect_for_storage(json.dumps(payload, ensure_ascii=False)))
        Path(name).replace(destination)
    finally:
        Path(name).unlink(missing_ok=True)
    return tuple(pages)


def pages_ready(pages: tuple[ExtractedPage, ...]) -> bool:
    return bool(pages) and any(p.status == "READY" for p in pages) and all(p.status in {"READY", "BLANK"} for p in pages)
