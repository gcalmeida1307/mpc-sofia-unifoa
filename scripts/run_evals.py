"""Run a small, reproducible retrieval smoke evaluation for every module.

This reports measured corpus/retrieval availability, not a fabricated LLM
quality percentage.  Add gold cases to tests/evals/manifest.json as the
institution accumulates reviewed examples.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.evaluation import evaluate_corpus

KNOWLEDGE = ROOT / "knowledge"


def main() -> int:
    import json

    print(json.dumps(evaluate_corpus(KNOWLEDGE), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
