import os
from pathlib import Path


DEFAULT_DOCS_ROOT = Path("/app/docs")
FALLBACK_DOCS_ROOT = Path(__file__).resolve().parents[1] / ".." / "docs"
DOCS_ROOT = DEFAULT_DOCS_ROOT if DEFAULT_DOCS_ROOT.exists() else FALLBACK_DOCS_ROOT


def get_knowledge_index():
    return {
        "module": "Knowledge",
        "indexed_sources": [
            "Markdown",
            "PDF",
            "DOCX",
            "Wiki",
            "Runbooks",
            "GLPI",
            "RFC",
            "Scripts",
            "Histórico",
            "Incidentes",
        ],
        "search_backend": "Qdrant (planejado)",
        "status": "indexing-ready",
    }


def ingest_source(payload: dict):
    return {
        "status": "queued",
        "source": payload.get("source"),
        "source_type": payload.get("source_type"),
        "path": payload.get("path"),
        "metadata": payload.get("metadata") or {},
        "message": "Documento recebido para indexação pelo módulo Knowledge.",
    }


def _iter_docs():
    if not DOCS_ROOT.exists():
        return []
    return [path for path in DOCS_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}]


def _shorten_text(text: str, limit: int = 180) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def search_knowledge(query: str):
    search_terms = query.lower().split()
    results = []
    for doc_path in _iter_docs():
        try:
            text = doc_path.read_text(encoding="utf-8")
        except Exception:
            continue

        lowered = text.lower()
        score = sum(1 for term in search_terms if term in lowered)
        if score > 0:
            snippet = _shorten_text(text.replace("\n", " "))
            results.append({
                "source": str(doc_path.relative_to(DOCS_ROOT)),
                "score": round(score / max(len(search_terms), 1), 2),
                "snippet": snippet,
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    return {"query": query, "results": results[:5]}
