import asyncio
import json
from pathlib import Path

from api.expansion import record_document_pipeline
from api.orchestration import answer
from api.providers import Generation
from api.retrieval import warm_module_index
from api.semantic_planner import interpret, parse_plan


def test_semantic_plan_is_bounded_and_cannot_change_deterministic_route() -> None:
    deterministic = {
        "intent": "DOCUMENT_RAG",
        "theme": "jornada de trabalho",
        "retrieval_required": True,
    }
    plan = parse_plan(
        json.dumps(
            {
                "intent": "CONVERSA_DIRETA",
                "topic": "jornada de trabalho",
                "concepts": ["hora extra", "hora extra", "\n\x00compensação"],
                "search_terms": ["limite diário"],
                "entities": ["pessoa@example.com", "SAAE"],
                "subqueries": ["qual é a regra aplicável?"],
                "confidence": 4,
            },
            ensure_ascii=False,
        ),
        deterministic,
    )

    assert plan.status == "ollama"
    assert plan.intent == "DOCUMENT_RAG"
    assert plan.concepts == ("hora extra", "compensação")
    assert plan.confidence == 1.0
    assert "pessoa@example.com" not in plan.provider_context()


def test_semantic_plan_invalid_output_falls_back_without_exception() -> None:
    plan = parse_plan("não é json", {"intent": "COMPARACAO_DOCUMENTOS", "retrieval_required": True})

    assert plan.status == "deterministic"
    assert plan.intent == "COMPARACAO_DOCUMENTOS"
    assert "JSON" in plan.reason


def test_local_ollama_interprets_once_and_retrieval_remains_the_authority(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SOFIA_OLLAMA_SEMANTIC_PLANNER", "always")
    monkeypatch.setenv("SOFIA_EMBEDDINGS_QUERY_ENABLED", "false")
    monkeypatch.setenv("SOFIA_STORAGE_MODE", "developer")
    # Other integration tests may exercise the real local endpoint first. A
    # test must explicitly start with a closed local circuit so this contract
    # validates the successful planner branch deterministically.
    monkeypatch.setattr("api.semantic_planner._SEMANTIC_FAILURE_UNTIL", 0.0)

    calls: list[str] = []

    async def fake_generate(provider: str, system: str, prompt: str, history: list[dict[str, str]], **kwargs: object) -> Generation:
        calls.append(prompt)
        assert provider == "ollama"
        assert "não consulte documentos" in system
        return Generation(
            json.dumps(
                {
                    "intent": "CONVERSA_DIRETA",
                    "topic": "política de backup",
                    "concepts": ["backup", "retenção"],
                    "search_terms": ["servidor Atlas", "30 dias"],
                    "entities": [],
                    "subqueries": [],
                    "confidence": 0.91,
                },
                ensure_ascii=False,
            ),
            "ollama",
            "qwen3.5:4b",
        )

    monkeypatch.setattr("api.semantic_planner.generate", fake_generate)
    root = tmp_path / "knowledge"
    path = root / "infraestrutura" / "manual_atlas.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "Manual do servidor Atlas. O backup deve ser diário e a retenção mínima é de 30 dias.",
        encoding="utf-8",
    )
    assert record_document_pipeline(root, "infraestrutura", path)["status"] == "READY"
    warm_module_index(root, "infraestrutura", force=True)

    question = "Explique, segundo o manual local, a política do servidor Atlas, a retenção do backup e a razão dessa regra."
    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question=question,
            history=[],
            external_allowed=False,
        )
    )

    assert len(calls) == 1
    assert response.context_package["semantic_interpretation"]["status"] == "ollama"
    assert response.context_package["semantic_interpretation"]["intent"] == "DOCUMENT_RAG"
    assert response.sources == ["manual_atlas.md"]
    assert "30 dias" in response.answer
    assert response.model in {"local-rag", "local-source-evidence", "evidence-summary", "extractive-evidence"}


def test_semantic_interpretation_is_cached_without_writing_raw_question(monkeypatch) -> None:
    monkeypatch.setenv("SOFIA_OLLAMA_SEMANTIC_PLANNER", "always")
    monkeypatch.setattr("api.semantic_planner._SEMANTIC_FAILURE_UNTIL", 0.0)
    calls: list[str] = []

    async def fake_generate(*args: object, **kwargs: object) -> Generation:
        calls.append("called")
        return Generation(
            '{"intent":"DOCUMENT_RAG","topic":"backup","concepts":["retenção"],"confidence":0.8}',
            "ollama",
            "qwen3.5:4b",
        )

    monkeypatch.setattr("api.semantic_planner.generate", fake_generate)
    deterministic = {"intent": "DOCUMENT_RAG", "retrieval_required": True}
    question = "Pergunta privada com contato pessoa-cache@example.com sobre backup e retenção"
    first = asyncio.run(interpret("infraestrutura", question, deterministic))
    second = asyncio.run(interpret("infraestrutura", question, deterministic))

    assert first == second
    assert len(calls) == 1
    assert "pessoa-cache@example.com" not in second.provider_context()
