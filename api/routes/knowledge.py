from fastapi import APIRouter
from pydantic import BaseModel

from services.knowledge import get_knowledge_index, ingest_source, search_knowledge

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


class KnowledgeIngestRequest(BaseModel):
    source: str
    source_type: str
    path: str | None = None
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


@router.post("/ingest")
def ingest(payload: KnowledgeIngestRequest):
    return ingest_source(payload.model_dump())


@router.get("/search")
def search(query: str):
    return search_knowledge(query)
