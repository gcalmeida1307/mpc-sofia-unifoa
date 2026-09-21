"""Blind regression cases for documents and vocabulary absent from the CORE.

These cases deliberately use invented names.  A pass must come from the
generic ingestion, structural chunking and retrieval contracts, not from a
domain-specific keyword branch.
"""

from pathlib import Path

from api.ingestion import ingest_module
from api.policies import policy_for
from api.query_analysis import QueryPlan, route_query
from api.retrieval import retrieve, warm_module_index


def _document(root: Path, name: str, text: str) -> Path:
    path = root / "financeiro" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_blind_document_fact_is_retrieved_without_domain_keywords(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    path = _document(
        root,
        "protocolo_aurora.md",
        "# Protocolo Aurora\n\nO código Lumina deve ser confirmado antes da etapa seguinte.\n\nA confirmação válida dura 48 horas.",
    )
    warm_module_index(root, "financeiro", force=True)

    result = retrieve(
        root,
        "financeiro",
        "O que o arquivo protocolo_aurora.md diz sobre o código Lumina?",
        policy_for("financeiro"),
    )

    assert result.has_quality_evidence
    assert path.name in result.sources
    assert "Lumina" in result.context


def test_blind_structural_units_preserve_sections_for_summary(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    path = _document(
        root,
        "manual_orion.md",
        "# Manual Orion\n\n## Origem\n\nO sistema nasceu no ciclo inicial.\n\n## Fluxo\n\nA etapa seguinte valida o selo âmbar.\n\n## Limites\n\nO prazo máximo é de 72 horas.",
    )
    chunks = ingest_module(root, "financeiro", selected_paths=(path,))

    headers = {chunk.section_header for chunk in chunks}
    assert "Origem" in headers
    assert "Fluxo" in headers
    assert "Limites" in headers

    warm_module_index(root, "financeiro", force=True)
    result = retrieve(root, "financeiro", "Resuma o documento manual_orion.md.", policy_for("financeiro"))
    assert result.has_quality_evidence
    assert len(result.evidence) >= 3


def test_blind_concept_comparison_uses_a_distinct_plan(tmp_path: Path) -> None:
    payload = route_query(
        "financeiro",
        "Compare os conceitos Delta e Sigma no arquivo protocolo_aurora.md.",
    )
    plan = QueryPlan.from_mapping(
        payload["query_plan"],
        fallback_intent="DOCUMENT_RAG",
        retrieval_required=True,
        response_mode="evidence",
    )

    assert plan.intent == "COMPARACAO_DOCUMENTOS"
    assert plan.strategy == "CONCEPT_COMPARISON"


def test_blind_multi_hop_and_rca_strategies_are_general() -> None:
    multi_hop = route_query(
        "financeiro",
        "Relacione a condição inicial com o resultado final e explique o que acontece depois.",
    )
    rca = route_query(
        "infraestrutura",
        "Faça uma investigação de causa raiz do incidente descrito no documento.",
    )

    assert multi_hop["query_plan"]["strategy"] == "MULTI_HOP"
    assert rca["query_plan"]["strategy"] == "RCA_INVESTIGATION"
