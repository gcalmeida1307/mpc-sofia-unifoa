from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.circuit_breaker import ProviderCircuitBreaker
from api.evaluation import golden_gate
from api.feedback_candidates import list_candidates, record_candidate, review_candidate
from api.job_queue import PersistentJobQueue
from api.neural import status as neural_status
from api.neural import train as train_neural
from api.privacy import ExternalRedaction
from api.retrieval import (
    activate_index_version,
    list_index_versions,
    rrf_fuse,
    stage_module_index,
    warm_module_index,
)


def test_rrf_fuses_rankings_without_replacing_exact_lexical_path() -> None:
    lexical_only = rrf_fuse([1.0, 0.9, 0.1])
    fused = rrf_fuse([1.0, 0.9, 0.1], [0.1, 1.0, 0.8])
    assert len(fused) == 3
    assert fused != lexical_only
    assert all(0.0 <= value <= 1.0 for value in fused)


def test_index_publication_has_atomic_pointer_and_rollback(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    source = root / "direito" / "lei.md"
    source.parent.mkdir(parents=True)
    source.write_text("Artigo um: regra antiga.", encoding="utf-8")
    first = warm_module_index(root, "direito", force=True)
    source.write_text("Artigo um: regra nova e atualizada.", encoding="utf-8")
    second = warm_module_index(root, "direito", force=True)
    versions = list_index_versions(root, "direito")
    assert first["manifest"]
    assert len(versions["versions"]) == 2
    assert versions["active"] != first["signature"][:20]
    rolled_back = activate_index_version(root, "direito", versions["versions"][-1])
    assert rolled_back["active"] == versions["versions"][-1]
    assert second["signature"]


def test_index_staging_does_not_change_active_version(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    source = root / "direito" / "lei.md"
    source.parent.mkdir(parents=True)
    source.write_text("Regra inicial.", encoding="utf-8")
    warm_module_index(root, "direito", force=True)
    active_before = list_index_versions(root, "direito")["active"]
    source.write_text("Regra candidata para aprovação.", encoding="utf-8")
    staged = stage_module_index(root, "direito", force=True)
    versions = list_index_versions(root, "direito")
    assert staged["status"] == "staged"
    assert versions["active"] == active_before
    assert versions["staged"] == staged["version"]


def test_job_queue_survives_retry_and_applies_backoff(tmp_path: Path) -> None:
    queue = PersistentJobQueue(tmp_path / "knowledge")
    job_id = queue.enqueue("neural_training", "direito", {"reason": "test"}, idempotency_key="same-job")
    assert queue.enqueue("neural_training", "direito", {}, idempotency_key="same-job") == job_id
    claimed = queue.claim("neural_training")
    assert claimed is not None
    assert claimed.attempts == 1
    failed = queue.fail(job_id, "timeout", backoff_seconds=30)
    assert failed is not None
    assert failed.status == "retry"
    assert queue.counts("neural_training")["retry"] == 1
    assert queue.pending("neural_training")[0].job_id == job_id


def test_circuit_breaker_opens_after_threshold_and_can_be_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOFIA_PROVIDER_FAILURE_THRESHOLD", "2")
    breaker = ProviderCircuitBreaker()
    assert breaker.allow("ollama")
    breaker.failure("ollama")
    assert breaker.allow("ollama")
    breaker.failure("ollama")
    assert not breaker.allow("ollama")
    breaker.reset("ollama")
    assert breaker.allow("ollama")


def test_entity_dictionary_masks_and_restores_request_scoped_values() -> None:
    redaction = ExternalRedaction()
    cleaned = redaction.clean_with_entities("Paciente Maria da Silva, CPF 123.456.789-00", ["Maria da Silva"])
    assert "Maria da Silva" not in cleaned
    assert "123.456.789-00" not in cleaned
    assert redaction.restore(cleaned) == "Paciente Maria da Silva, CPF 123.456.789-00"


def test_bad_feedback_is_isolated_until_human_review(tmp_path: Path) -> None:
    assessment = {
        "analytics_id": 7,
        "module_id": "direito",
        "theme": "jornada",
        "provider": "local-rag",
        "feedback": "bad",
        "source_names": ["lei.md"],
    }
    candidate = record_candidate(tmp_path / "knowledge", assessment)
    assert candidate["status"] == "pending_review"
    assert list_candidates(tmp_path / "knowledge", "direito")[0]["candidate_id"] == candidate["candidate_id"]
    reviewed = review_candidate(tmp_path / "knowledge", candidate["candidate_id"], "approved")
    assert reviewed["status"] == "approved"
    assert not (tmp_path / "knowledge" / "direito" / "lei.md").exists()


def test_autoencoder_is_explicitly_diagnostic_not_answer_ranking(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    source = root / "direito" / "lei.md"
    source.parent.mkdir(parents=True)
    source.write_text("Artigo sobre jornada e horas extras.", encoding="utf-8")
    trained = train_neural(root, "direito", epochs=1)
    current = neural_status(root, "direito")
    assert trained["purpose"] == "diagnostic_chunk_profile"
    assert trained["ranking_enabled"] is False
    assert current["ranking_enabled"] is False


def test_golden_gate_does_not_approve_draft_cases(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    (root / "direito").mkdir(parents=True)
    (root / "direito" / "lei.md").write_text("Regra sobre jornada.", encoding="utf-8")
    evals = tmp_path / "tests" / "evals"
    evals.mkdir(parents=True)
    (evals / "manifest.json").write_text(
        json.dumps({
            "version": "1",
            "modules": ["direito"],
            "cases": [{"module": "direito", "question": "qual regra?", "reviewed": False}],
        }),
        encoding="utf-8",
    )
    gate = golden_gate(root)
    assert gate["status"] == "blocked"
    assert gate["release_allowed"] is False


def test_fhir_r4_namespace_is_exposed_alongside_legacy_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    # Importing the FastAPI app loads the developer .env. Keep this contract
    # test isolated from PostgreSQL-backed temporary-root tests collected in
    # the same process.
    monkeypatch.setenv("SOFIA_POSTGRES_URL", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("SOFIA_STORAGE_MODE", "developer")
    from api.server import app

    paths = {route.path for route in app.routes}
    assert "/fhir/R4/metadata" in paths
    assert "/fhir/R4/{resource_type}" in paths
    assert "/fhir/R4/{resource_type}/{resource_id}" in paths
