"""Curated feedback boundary for evaluation work.

Feedback is a quality signal, not permission to rewrite the knowledge base.
Candidates are kept outside ``knowledge/`` and contain no prompt, answer or
clinical payload. Promotion to a golden case is an explicit administrative
operation with reviewed expectations.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_LOCK = threading.RLock()


def _path(root: Path, module_id: str) -> Path:
    return root.parent / "data" / "eval-candidates" / f"{module_id}.jsonl"


def record_candidate(root: Path, assessment: dict[str, Any]) -> dict[str, Any]:
    """Append a metadata-only candidate awaiting human review."""
    candidate = {
        "candidate_id": uuid.uuid4().hex,
        "analytics_id": int(assessment.get("analytics_id", 0)),
        "module_id": str(assessment.get("module_id", "")),
        "theme": str(assessment.get("theme", "")),
        "provider": str(assessment.get("provider", "")),
        "feedback": str(assessment.get("feedback", "bad")),
        "source_names": [str(item) for item in assessment.get("source_names", [])[:20]],
        "status": "pending_review",
        "created_at": datetime.now(UTC).isoformat(),
    }
    path = _path(root, candidate["module_id"])
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(candidate, ensure_ascii=False) + "\n")
    return candidate


def list_candidates(root: Path, module_id: str | None = None) -> list[dict[str, Any]]:
    paths = [_path(root, module_id)] if module_id else sorted((root.parent / "data" / "eval-candidates").glob("*.jsonl"))
    rows: list[dict[str, Any]] = []
    for path in paths:
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    if isinstance(item, dict):
                        rows.append(item)
        except (OSError, ValueError):
            continue
    return rows


def review_candidate(root: Path, candidate_id: str, decision: str) -> dict[str, Any]:
    """Record review state; approval alone never changes the eval manifest."""
    if decision not in {"approved", "rejected"}:
        raise ValueError("decision deve ser approved ou rejected")
    paths = sorted((root.parent / "data" / "eval-candidates").glob("*.jsonl"))
    with _LOCK:
        for path in paths:
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            changed = False
            updated_rows = []
            found = None
            for line in lines:
                if not line.strip():
                    continue
                item = json.loads(line)
                if item.get("candidate_id") == candidate_id:
                    item = {**item, "status": decision, "reviewed_at": datetime.now(UTC).isoformat()}
                    found = item
                    changed = True
                updated_rows.append(item)
            if changed:
                path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in updated_rows) + "\n", encoding="utf-8")
                return found
    raise ValueError("Candidato não encontrado")


__all__ = ["list_candidates", "record_candidate", "review_candidate"]

