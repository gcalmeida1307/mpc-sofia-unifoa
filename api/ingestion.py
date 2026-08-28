from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from pypdf import PdfReader

logger = logging.getLogger("sofia.ingestion")
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".pdf", ".docx"}


@dataclass(frozen=True)
class DocumentChunk:
    path: Path
    text: str
    ordinal: int


def files_for(root: Path, module_id: str) -> list[Path]:
    module_root = root / module_id
    return [p for p in module_root.rglob("*") if p.is_file() and p.name != ".gitkeep" and p.suffix.lower() in ALLOWED_EXTENSIONS]


def extract_text(path: Path) -> str:
    try:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        if suffix == ".docx":
            return "\n".join(paragraph.text for paragraph in Document(str(path)).paragraphs)
        if suffix == ".csv":
            rows = csv.reader(io.StringIO(path.read_text(encoding="utf-8", errors="ignore")))
            return "\n".join(" | ".join(row) for row in rows)
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return ""


def _paragraphs(text: str) -> list[str]:
    return [" ".join(part.split()) for part in text.replace("\r\n", "\n").split("\n\n") if part.strip()]


def ingest_module(root: Path, module_id: str, max_chars: int = 1800, overlap: int = 250) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in files_for(root, module_id):
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
                tail = current[-overlap:] if overlap else ""
                current = f"{tail}\n{unit}".strip()
            else:
                for start in range(0, len(unit), max_chars - overlap):
                    chunks.append(DocumentChunk(path, unit[start:start + max_chars], ordinal))
                    ordinal += 1
                current = ""
        if current:
            chunks.append(DocumentChunk(path, current, ordinal))
    return chunks
