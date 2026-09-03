"""Record a privacy-safe operational canary for every populated module.

The canary is not a fake user conversation and it does not measure answer
quality.  It proves that the observability store can persist a complete,
content-free execution envelope for a module before the release gate is run.
The request itself is stored only as a hash by ``TraceRecorder``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.domains import DOMAIN_CONTRACTS
from api.ingestion import files_for
from api.observability import TraceRecorder, initialize


def run() -> dict[str, object]:
    knowledge_root = ROOT / "knowledge"
    initialize(knowledge_root)
    rows: list[dict[str, object]] = []
    for module_id in sorted(DOMAIN_CONTRACTS):
        documents = files_for(knowledge_root, module_id)
        if not documents:
            rows.append({"module": module_id, "status": "skipped", "reason": "sem corpus local"})
            continue
        recorder = TraceRecorder(
            knowledge_root,
            module_id,
            f"readiness canary {module_id}",
            "AG000001",
        )
        for stage in ("perception", "routing", "planning", "retrieval", "reasoning", "critique", "delivery"):
            recorder.span(stage, "complete", {"canary": True})
        recorder.finish(
            status="READY",
            intent="readiness_canary",
            complexity="canary",
            router="production-gate",
            provider="readiness-canary",
            model="pipeline-gate",
            confidence=1.0,
            metrics={
                "canary": True,
                "source_count": len(documents),
                "tokens": 0,
                "cost": 0,
            },
        )
        rows.append({"module": module_id, "status": "recorded", "documents": len(documents)})
    return {"status": "completed", "modules": rows, "privacy": "request content is hashed; no prompt or answer is persisted"}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
