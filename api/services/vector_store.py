from __future__ import annotations

import json
from pathlib import Path


class SimpleVectorStore:
    def __init__(self, path: str | None = None):
        self.path = Path(path or "/tmp/sofia_vector_store.json")
        self._store: list[dict] = []
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self._store = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._store = []

    def _save(self):
        self.path.write_text(json.dumps(self._store, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, text: str, metadata: dict | None = None):
        self._store.append({"text": text, "metadata": metadata or {}})
        self._save()

    def add_many(self, items: list[tuple[str, dict | None]]):
        prepared = [{"text": text, "metadata": metadata or {}} for text, metadata in items if text.strip()]
        if not prepared:
            return
        self._store.extend(prepared)
        self._save()

    def search(self, query: str, limit: int = 3):
        q = query.lower()
        scored = []
        for item in self._store:
            text = (item.get("text") or "").lower()
            score = sum(1 for token in q.split() if token in text)
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda row: row[0], reverse=True)
        return [item for _, item in scored[:limit]]


vector_store = SimpleVectorStore()
