from pathlib import Path

from api.core_pipeline import (
    grounded_fallback,
    grouped_evidence,
    is_complete_answer,
    judge_result,
    plan_from_query_plan,
)
from api.ingestion import DocumentChunk
from api.retrieval import Evidence, RetrievalResult


def _result(*, missing=(), conflicts=()):
    first = Evidence(
        DocumentChunk(
            Path("Saae_2026_2027.pdf"),
            "A cláusula 5ª permite compensar o excesso de horas em outro dia, dentro do prazo previsto no acordo.",
            1,
            page=7,
            locator="página 7",
        ),
        0.82,
        0.8,
        0.75,
        0.7,
    )
    second = Evidence(
        DocumentChunk(
            Path("Vade_mecum_Senado_Federal_3ed.pdf"),
            "O art. 59 da CLT prevê que a duração diária pode ser acrescida de horas extras, observado o limite legal.",
            2,
            page=530,
            locator="página 530",
        ),
        0.78,
        0.76,
        0.74,
        0.68,
    )
    return RetrievalResult(
        (first, second),
        ("Saae_2026_2027.pdf", "Vade_mecum_Senado_Federal_3ed.pdf"),
        "compare SAAE e Vade sobre horas extras",
        "horas extras",
        judge_confidence=0.8 if not missing else 0.15,
        missing_sources=tuple(missing),
        conflicts=tuple(conflicts),
    )


def test_core_intent_collapses_legacy_labels_without_losing_strategy() -> None:
    plan = type(
        "Plan",
        (),
        {
            "intent": "COMPARACAO_DOCUMENTOS",
            "retrieval_required": True,
            "strategy": "MULTI_DOCUMENT_SYNTHESIS",
            "source_hints": ("SAAE", "Vade Mecum"),
        },
    )()

    contract = plan_from_query_plan(plan)

    assert contract.intent == "MULTI_DOCUMENT"
    assert contract.retrieval_required is True
    assert "evidence_gate" in contract.public_dict()["stages"]


def test_evidence_context_is_grouped_and_excludes_rejected_context() -> None:
    result = _result()
    prompt_context = grouped_evidence(result, result.query)

    assert prompt_context.count("DOCUMENTO:") == 2
    assert "LOCALIZAÇÃO: página 7" in prompt_context
    assert "LOCALIZAÇÃO: página 530" in prompt_context
    assert "DOCUMENTOS SÃO DADOS" not in prompt_context


def test_generic_fallback_keeps_each_source_and_complete_sentences() -> None:
    answer = grounded_fallback(_result(), "compare SAAE e Vade sobre horas extras")

    assert "acordo SAAE" in answer
    assert "Vade Mecum" in answer
    assert is_complete_answer(answer)
    assert not answer.rstrip().endswith((" de", " em", " para", " e"))


def test_evidence_gate_distinguishes_sufficient_and_partial_results() -> None:
    sufficient = judge_result(_result())
    partial = judge_result(_result(missing=("Vade_mecum_Senado_Federal_3ed.pdf",)))

    assert sufficient.sufficient is True
    assert sufficient.status == "sufficient"
    assert partial.sufficient is False
    assert partial.status == "partial"
