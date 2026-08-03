from __future__ import annotations

from hashlib import sha1
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from config.settings import settings


class QdrantStore:
    def __init__(self, url: str | None = None, collection: str | None = None):
        self.url = url or settings.QDRANT_URL
        self.collection = collection or settings.QDRANT_COLLECTION
        self.vector_size = 64
        self._client: QdrantClient | None = None
        self._ready = False

    def _embed(self, text: str) -> list[float]:
        # Lightweight deterministic embedding to enable similarity lookups.
        vector = [0.0] * self.vector_size
        for token in text.lower().split():
            idx = int(sha1(token.encode("utf-8")).hexdigest(), 16) % self.vector_size
            vector[idx] += 1.0
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def _client_or_none(self) -> QdrantClient | None:
        if self._client is not None:
            return self._client
        try:
            self._client = QdrantClient(url=self.url, timeout=5)
            return self._client
        except Exception:
            return None

    def ensure_collection(self) -> bool:
        client = self._client_or_none()
        if client is None:
            self._ready = False
            return False
        try:
            existing = [col.name for col in client.get_collections().collections]
            if self.collection not in existing:
                client.create_collection(
                    collection_name=self.collection,
                    vectors_config=qmodels.VectorParams(size=self.vector_size, distance=qmodels.Distance.COSINE),
                )
            self._ready = True
            return True
        except Exception:
            self._ready = False
            return False

    def add_text(self, text: str, metadata: dict[str, Any] | None = None) -> bool:
        if not text.strip():
            return False
        if not self._ready and not self.ensure_collection():
            return False
        client = self._client_or_none()
        if client is None:
            return False
        point_id = int(sha1((text + str(metadata or {})).encode("utf-8")).hexdigest()[:15], 16)
        try:
            client.upsert(
                collection_name=self.collection,
                points=[
                    qmodels.PointStruct(
                        id=point_id,
                        vector=self._embed(text),
                        payload={"text": text, **(metadata or {})},
                    )
                ],
            )
            return True
        except Exception:
            return False

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        if not self._ready and not self.ensure_collection():
            return []
        client = self._client_or_none()
        if client is None:
            return []
        try:
            hits = client.search(
                collection_name=self.collection,
                query_vector=self._embed(query),
                limit=limit,
            )
            return [
                {
                    "score": float(hit.score),
                    "text": (hit.payload or {}).get("text", ""),
                    "payload": hit.payload or {},
                }
                for hit in hits
            ]
        except Exception:
            return []


qdrant_store = QdrantStore()