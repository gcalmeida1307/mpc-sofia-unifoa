from __future__ import annotations

import tempfile
from pathlib import Path

from api.observability import TraceRecorder, snapshot


def test_trace_store_keeps_operational_metadata_without_the_question() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "knowledge"
        secret_question = "cpf 123.456.789-09 não deve ser armazenado"
        trace = TraceRecorder(root, "direito", secret_question, "AG000001")
        trace.span("retrieve", "complete", {"sources": 1})
        trace.finish(provider="local-rag", model="tfidf-local", confidence=0.8)
        result = snapshot(root)
        assert result["total"] == 1
        row = result["traces"][0]
        assert row["request_hash"]
        assert secret_question not in str(row)
        assert row["status"] == "READY"

