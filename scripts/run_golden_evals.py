"""Run the hard, reviewed-evidence gate used before publishing an index."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.evaluation import golden_gate


def main() -> int:
    result = golden_gate(ROOT / "knowledge")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["release_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

