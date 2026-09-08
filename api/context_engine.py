"""Context package and answer verification boundary for the intelligence core."""

from __future__ import annotations

import re
from pathlib import Path

from .contracts import ContextPackage, EvidenceContract, VerificationResult
from .domains import domain_for
from .query_analysis import classify_query, normalize
from .retrieval import RetrievalResult


def complexity_for(question: str, evidence_count: int = 0) -> str:
    text = normalize(question)
    if len(text.split()) <= 8 and evidence_count <= 2 and not any(marker in text for marker in ("compar", "relac", "contrad", "cenar", "analis")):
        return "L1"
    if any(marker in text for marker in ("execute", "executar", "crie", "adicionar host", "sincroniz")):
        return "L4"
    if any(marker in text for marker in ("compare", "comparar", "brecha", "jurisprud", "contradiz", "cenário", "cenario")):
        return "L3"
    return "L2" if evidence_count else "L1"


def build_context_package(
    module_id: str,
    question: str,
    result: RetrievalResult,
    history: list[dict[str, str]] | None = None,
    expected_response_type: str = "structured",
    root: Path | None = None,
) -> ContextPackage:
    profile = classify_query(module_id, question)
    contract = domain_for(module_id)
    accepted = [
        EvidenceContract(
            source=item.chunk.path.name,
            ordinal=item.chunk.ordinal,
            score=round(float(item.score), 4),
            lexical_score=round(float(item.lexical_score), 4),
            semantic_score=round(float(item.semantic_score), 4),
            coverage=round(float(item.coverage), 4),
            accepted=True,
            reason="atingiu o gate de relevância e cobertura",
            authority_score=round(float(item.authority_score), 4),
            freshness_score=round(float(item.freshness_score), 4),
            provenance_score=round(float(item.provenance_score), 4),
            support_score=round(float(item.support_score), 4),
            contradiction_score=round(float(item.contradiction_score), 4),
        )
        for item in result.evidence
    ]
    rejected = [
        EvidenceContract(
            source=item.chunk.path.name,
            ordinal=item.chunk.ordinal,
            score=round(float(item.score), 4),
            lexical_score=round(float(item.lexical_score), 4),
            semantic_score=round(float(item.semantic_score), 4),
            coverage=round(float(item.coverage), 4),
            accepted=False,
            reason=item.rejection_reason or "rejeitada pelo Evidence Judge",
            authority_score=round(float(item.authority_score), 4),
            freshness_score=round(float(item.freshness_score), 4),
            provenance_score=round(float(item.provenance_score), 4),
            support_score=round(float(item.support_score), 4),
            contradiction_score=round(float(item.contradiction_score), 4),
        )
        for item in result.rejected_evidence
    ]
    context_text = normalize(result.context)
    candidate_terms = list(dict.fromkeys([*contract.keywords, *re.findall(r"[\wÀ-ÿ]{4,}", normalize(question))]))
    present = [term for term in candidate_terms if len(normalize(term)) >= 4 and normalize(term) in context_text]
    relations: list[dict[str, object]] = []
    for index, left in enumerate(present[:16]):
        for right in present[index + 1 : 16]:
            relations.append(
                {
                    "from": left,
                    "to": right,
                    "type": "co_occurrence",
                    "confidence": 0.62,
                    "status": "observed",
                    "evidence_count": len(accepted),
                }
            )
            if len(relations) >= 24:
                break
        if len(relations) >= 24:
            break
    if root is not None:
        try:
            from .knowledge_graph import read_graph

            graph = read_graph(root, module_id)
            graph_edges = [
                {
                    "from": item.get("source"),
                    "to": item.get("target"),
                    "type": item.get("relation", "related_to"),
                    "confidence": item.get("confidence", 0.0),
                    "provenance": item.get("provenance", []),
                    "status": "observed",
                }
                for item in graph.get("edges", [])
                if isinstance(item, dict)
            ]
            relations.extend(graph_edges[:24])
        except (OSError, RuntimeError, ValueError, TypeError):
            pass
    return ContextPackage(
        question=question,
        domain=module_id,
        intent=str(profile.get("intent", "module_knowledge_lookup")),
        complexity=complexity_for(question, len(accepted)),
        risk="high" if contract.high_risk else "standard",
        conversation_context=(history or [])[-6:],
        accepted_evidence=accepted,
        rejected_evidence=rejected,
        relations=relations,
        conflicts=list(result.conflicts),
        available_tools=list(contract.tools),
        domain_policy={
            "high_risk": contract.high_risk,
            "require_citation": contract.require_citation,
            "allow_general_knowledge": contract.allow_general_knowledge,
            "source_profile": contract.source_profile,
            "evidence_judge": "relevance+authority+freshness+provenance+support+conflict",
        },
        expected_response_type=expected_response_type,
        route=str(profile.get("route", "evidence")),
        retrieval_required=bool(profile.get("retrieval_required", True)),
        response_mode=str(profile.get("response_mode", "evidence")),
        required_sources=list(result.required_sources),
        missing_sources=list(result.missing_sources),
    )


def verify_answer(answer: str, result: RetrievalResult, module_id: str) -> VerificationResult:
    """Lightweight claim/evidence gate; never exposes chain-of-thought."""
    if not answer.strip():
        return VerificationResult("rejected", 0.0, ["resposta vazia"], ["provider não retornou conteúdo"])
    if not result.evidence:
        return VerificationResult("unverified", 0.25, [], ["não há evidência local aceita"])
    evidence_text = normalize(result.context)
    evidence_terms = set(re.findall(r"[\wÀ-ÿ]{4,}", evidence_text))
    answer_terms = set(re.findall(r"[\wÀ-ÿ]{4,}", normalize(answer)))
    overlap = len(answer_terms & evidence_terms) / max(1, len(answer_terms))
    warnings: list[str] = []
    if result.conflicts:
        warnings.append(f"{len(result.conflicts)} possível(is) conflito(s) textual(is) exige(m) revisão")
    if module_id == "medicina" and any(marker in normalize(answer) for marker in ("diagnostico definitivo", "tome ", "prescrevo")):
        warnings.append("linguagem clínica incompatível com apoio informacional")
    claim_units = [
        unit.strip(" -*•\t")
        for unit in re.split(r"(?:\n+|(?<=[.!?])\s+)", normalize(answer))
        if len(unit.strip()) >= 35
        and not unit.strip().startswith((
            "conclusao",
            "base documental",
            "pontos de atencao",
            "limites",
            "proximo passo",
            "origem da resposta",
        ))
    ]
    unsupported: list[str] = []
    claim_scores: list[float] = []
    stopwords = {
        "essa", "esse", "isso", "apenas", "sobre", "quando", "documento", "documentos",
        "fonte", "fontes", "resposta", "tambem", "pode", "podem", "deve", "devem",
    }
    for claim in claim_units:
        claim_terms = {
            term for term in re.findall(r"[\wÀ-ÿ]{4,}", claim)
            if term not in stopwords
        }
        if not claim_terms:
            continue
        claim_overlap = len(claim_terms & evidence_terms) / max(1, len(claim_terms))
        claim_scores.append(claim_overlap)
        # Numeric/legal claims need an exact counterpart in the evidence; a
        # generic word overlap is not enough to validate a deadline, amount or
        # article number.
        numeric_claims = set(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", claim))
        numeric_evidence = set(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", evidence_text))
        if claim_overlap < 0.12 or (numeric_claims and not numeric_claims <= numeric_evidence):
            unsupported.append(claim[:180])
    if (
        overlap < 0.08
        or unsupported
        or any(item.support_score and item.support_score < 0.12 for item in result.evidence)
    ):
        confidence = max(0.2, min(0.85, (sum(claim_scores) / len(claim_scores)) if claim_scores else overlap))
        return VerificationResult("repaired", confidence, unsupported[:5] or ["alegações com baixa sustentação textual"], warnings)
    judge_confidence = getattr(result, "judge_confidence", 0.0)
    claim_confidence = sum(claim_scores) / len(claim_scores) if claim_scores else overlap
    return VerificationResult("verified", min(0.99, max(0.45 + overlap, claim_confidence, judge_confidence)), [], warnings)
