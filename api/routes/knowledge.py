import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from services.knowledge import (
    get_knowledge_index,
    ingest_source,
    list_knowledge_sources,
    refresh_due_knowledge_sources,
    register_knowledge_source,
    search_knowledge,
)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_UPLOAD_SUFFIXES = {".txt", ".md", ".pdf", ".docx"}


class KnowledgeIngestRequest(BaseModel):
    source: str
    source_type: str
    path: str | None = None
    url: str | None = None
    max_pages: int | None = None
    max_depth: int | None = None
    metadata: dict | None = None


class KnowledgeProviderRequest(BaseModel):
    name: str | None = None
    label: str | None = None
    url: str
    enabled: bool = True
    refresh_seconds: int | None = None
    allowed_domains: list[str] | None = None
    allowed_paths: list[str] | None = None
    metadata: dict | None = None


@router.get("/status")
def status():
    return {
        "module": "Knowledge",
        "status": "ready",
        "sources": ["Markdown", "PDF", "DOCX", "Wiki", "Runbooks", "GLPI", "RFC", "Scripts", "Histórico", "Incidentes"],
    }


@router.get("/index")
def index():
    return get_knowledge_index()


@router.get("/providers")
def providers():
    return list_knowledge_sources()


@router.post("/providers")
def providers_create(payload: KnowledgeProviderRequest):
    return register_knowledge_source(payload.model_dump())


@router.post("/providers/refresh")
def providers_refresh(force: bool = False):
    return refresh_due_knowledge_sources(force=force)


@router.post("/ingest")
def ingest(payload: KnowledgeIngestRequest):
    return ingest_source(payload.model_dump())


@router.post("/ingest/site")
def ingest_site(payload: KnowledgeIngestRequest):
    return ingest_source({**payload.model_dump(), "source_type": payload.source_type or "documentation_site"})


@router.post("/upload")
async def upload_training_asset(
    file: UploadFile = File(...),
    source: str = Form("user-upload"),
    metadata: str = Form("{}"),
):
    try:
        parsed_metadata = json.loads(metadata) if metadata else {}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"invalid metadata JSON: {exc}") from exc

    content = await file.read()
    suffix = ("." + (file.filename or "").rsplit(".", 1)[-1].lower()) if "." in (file.filename or "") else ""
    if suffix not in ALLOWED_UPLOAD_SUFFIXES:
        raise HTTPException(status_code=415, detail="tipo de arquivo não permitido")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="arquivo excede o limite de 10 MB")
    return ingest_source(
        {
            "source": source,
            "source_type": "upload",
            "file_name": file.filename or source,
            "content_bytes": content,
            "metadata": parsed_metadata,
        }
    )


@router.get("/search")
def search(query: str):
    return search_knowledge(query)
