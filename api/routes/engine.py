from fastapi import APIRouter
from pydantic import BaseModel

from services.docker_service import DockerService
from services.persistence import persistence
from services.postgres_store import postgres_store
from services.qdrant_store import qdrant_store
from services.vector_store import vector_store

router = APIRouter(prefix="/engine", tags=["Engine"])


class EngineRequest(BaseModel):
    text: str


@router.post("/ingest")
def ingest(payload: EngineRequest):
    vector_store.add(payload.text, {"source": "manual"})
    postgres_store.add_message("system", payload.text, {"source": "manual_ingest"})
    qdrant_store.add_text(payload.text, {"source": "manual_ingest"})
    return {"status": "indexed", "stored": payload.text}


@router.get("/history")
def history():
    sql_history = postgres_store.get_recent_messages(limit=30)
    if sql_history:
        return {"history": sql_history, "backend": "postgres"}
    return {"history": persistence.get_history(), "backend": "json-fallback"}


@router.get("/memory/status")
def memory_status():
    return {
        "postgres": {"ready": postgres_store.ensure_schema()},
        "qdrant": {"ready": qdrant_store.ensure_collection()},
    }


@router.get("/memory/search")
def memory_search(query: str):
    hits = qdrant_store.search(query, limit=5)
    if not hits:
        hits = [
            {
                "score": 0.0,
                "text": item.get("text", ""),
                "payload": item.get("metadata", {}),
            }
            for item in vector_store.search(query, limit=5)
        ]
    return {
        "query": query,
        "hits": hits,
    }


@router.post("/docker/list")
def docker_list():
    return {"containers": DockerService().list_containers()}
