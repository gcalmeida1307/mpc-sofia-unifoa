"""Conservative insight foundation based on persisted knowledge artifacts."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .expansion import ExpansionStore


def _connect(root: Path) -> sqlite3.Connection:
    path = root.parent / "data" / "insights.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("CREATE TABLE IF NOT EXISTS insights (id INTEGER PRIMARY KEY AUTOINCREMENT, module_id TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL, evidence_json TEXT NOT NULL, entities_json TEXT NOT NULL, confidence REAL NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_insights_module_date ON insights(module_id, created_at DESC)")
    connection.commit()
    return connection


def generate_module_insights(root: Path, module_id: str) -> dict[str, Any]:
    artifacts = ExpansionStore(root).pipeline_documents(module_id, 500)
    concept_sources: dict[str, set[str]] = {}
    for document in artifacts:
        raw = document.get("concepts_json") or document.get("artifacts", {}).get("concepts_json") or "[]"
        try:
            concepts = json.loads(raw) if isinstance(raw, str) else raw
        except (TypeError, ValueError):
            concepts = []
        for concept in concepts if isinstance(concepts, list) else []:
            concept_sources.setdefault(str(concept), set()).add(str(document.get("file_name", "")))
    pairs = Counter()
    concepts = sorted(concept_sources)
    for index, left in enumerate(concepts):
        for right in concepts[index + 1 :]:
            overlap = concept_sources[left] & concept_sources[right]
            if overlap:
                pairs[(left, right)] += len(overlap)
    rows: list[dict[str, Any]] = []
    connection = _connect(root)
    try:
        for (left, right), shared in pairs.most_common(30):
            confidence = min(0.95, 0.50 + shared * 0.08)
            item = {"kind": "relation", "title": f"Relação observada: {left} ↔ {right}", "evidence": sorted(concept_sources[left] | concept_sources[right]), "entities": [left, right], "confidence": confidence, "status": "observed"}
            connection.execute("INSERT INTO insights (module_id, kind, title, evidence_json, entities_json, confidence, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (module_id, item["kind"], item["title"], json.dumps(item["evidence"], ensure_ascii=False), json.dumps(item["entities"], ensure_ascii=False), confidence, item["status"], datetime.now(UTC).isoformat()))
            rows.append(item)
        connection.commit()
    finally:
        connection.close()
    return {"module_id": module_id, "generated": len(rows), "insights": rows, "note": "Relações são observações de coocorrência; não representam causalidade."}


def snapshot(root: Path, module_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    connection = _connect(root)
    try:
        where = "WHERE module_id = ?" if module_id else ""
        args = (module_id, max(1, min(500, limit))) if module_id else (max(1, min(500, limit)),)
        rows = connection.execute(f"SELECT * FROM insights {where} ORDER BY created_at DESC LIMIT ?", args).fetchall()
        return {"module_id": module_id, "insights": [dict(row) for row in rows], "count": len(rows)}
    finally:
        connection.close()

