from __future__ import annotations

import tempfile
from pathlib import Path

from api.context_engine import build_context_package
from api.expansion import pipeline_documents, record_document_pipeline
from api.policies import policy_for
from api.retrieval import retrieve


def test_document_canary_runs_from_received_to_ready_and_is_retrievable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "knowledge"
        path = root / "direito" / "textos" / "canario.txt"
        path.parent.mkdir(parents=True)
        path.write_text(
            "O acordo coletivo estabelece jornada de trabalho, compensação de horas e adicional de cinquenta por cento. "
            "A cláusula deve ser interpretada conforme a legislação aplicável.",
            encoding="utf-8",
        )
        result = record_document_pipeline(root, "direito", path)
        assert result["status"] == "READY"
        document = pipeline_documents(root, "direito")[0]
        assert document["status"] == "READY"
        assert document["current_stage"] == "READY"
        assert document["summary"]
        assert json_list(document["concepts_json"])
        stages = {event["stage"] for event in document["events"]}
        assert {"RECEIVED", "QUALITY_CHECK", "MARKDOWN_READY", "UNDERSTANDING", "CHUNKING", "EMBEDDING", "RELATING", "INDEXING", "VALIDATING"} <= stages
        retrieval = retrieve(root, "direito", "O que o acordo diz sobre compensação de horas?", policy_for("direito"), limit=3)
        assert retrieval.evidence
        package = build_context_package("direito", "O que o acordo diz sobre compensação?", retrieval)
        assert package.domain == "direito"
        assert package.accepted_evidence


def json_list(value: str) -> list[object]:
    import json

    decoded = json.loads(value)
    assert isinstance(decoded, list)
    return decoded

