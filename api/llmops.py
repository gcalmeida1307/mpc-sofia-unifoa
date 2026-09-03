"""Small, auditable runtime version contract for the SOFIA pipeline.

The values identify the rules that produced an answer without storing its
question or response. This makes a regression reproducible after a prompt,
retriever, artifact or orchestration change.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any


def runtime_versions() -> dict[str, str]:
    return {
        "app": os.getenv("SOFIA_APP_VERSION", "local"),
        "prompt": os.getenv("SOFIA_PROMPT_VERSION", "1.0"),
        "retrieval": "domain-packages-v1+evidence-judge-v1",
        "artifacts": "document-intelligence-v1.1",
        "orchestration": "bounded-harness-v1",
        "graph": "evidence-graph-v1",
    }


def request_fingerprint(module_id: str, question: str, provider: str) -> str:
    """Create a non-reversible correlation key for operational diagnostics."""
    value = f"{module_id}\x00{provider}\x00{question.strip().casefold()}".encode()
    return hashlib.sha256(value).hexdigest()[:24]


def trace_metrics(module_id: str, question: str, provider: str, **metrics: Any) -> dict[str, Any]:
    return {
        **metrics,
        "request_fingerprint": request_fingerprint(module_id, question, provider),
        "runtime_versions": runtime_versions(),
    }
