from __future__ import annotations

import json
from pathlib import Path


class SimplePersistence:
    def __init__(self, path: str | None = None):
        self.path = Path(path or "/tmp/sofia_persistence.json")
        self._data: list[dict] = []
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._data = []

    def _save(self):
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_message(self, role: str, text: str):
        self._data.append({"role": role, "text": text})
        self._save()

    def get_history(self):
        return list(self._data)


persistence = SimplePersistence()
