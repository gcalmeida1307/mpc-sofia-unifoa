from __future__ import annotations

from services.postgres_store import postgres_store
from services.qdrant_store import qdrant_store
from services.vector_store import vector_store


def get_memory_context(question: str, history_limit: int = 6, semantic_limit: int = 3) -> dict:
    history = postgres_store.get_recent_messages(limit=history_limit)
    semantic = qdrant_store.search(question, limit=semantic_limit)

    if not semantic:
        try:
            semantic = [
                {
                    "score": 0.0,
                    "text": item.get("text", ""),
                    "payload": item.get("metadata", {}),
                }
                for item in vector_store.search(question, limit=semantic_limit)
            ]
        except Exception:
            semantic = []

    return {
        "history": history,
        "semantic": semantic,
    }
