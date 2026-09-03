"""Context package and answer verification boundary for the intelligence core."""

from __future__ import annotations

import re

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
        )
        for item in result.evidence
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
    return ContextPackage(
        question=question,
        domain=module_id,
        intent=str(profile.get("intent", "module_knowledge_lookup")),
        complexity=complexity_for(question, len(accepted)),
        risk="high" if contract.high_risk else "standard",
        conversation_context=(history or [])[-6:],
        accepted_evidence=accepted,
        rejected_evidence=[],
        relations=relations,
        conflicts=[],
        available_tools=list(contract.tools),
        domain_policy={
            "high_risk": contract.high_risk,
            "require_citation": contract.require_citation,
            "allow_general_knowledge": contract.allow_general_knowledge,
            "source_profile": contract.source_profile,
        },
        expected_response_type=expected_response_type,
    )


def verify_answer(answer: str, result: RetrievalResult, module_id: str) -> VerificationResult:
    """Lightweight claim/evidence gate; never exposes chain-of-thought."""
    if not answer.strip():
        return VerificationResult("rejected", 0.0, ["resposta vazia"], ["provider não retornou conteúdo"])
    if not result.evidence:
        return VerificationResult("unverified", 0.25, [], ["não há evidência local aceita"])
    evidence_terms = set(re.findall(r"[\wÀ-ÿ]{4,}", normalize(result.context)))
    answer_terms = set(re.findall(r"[\wÀ-ÿ]{4,}", normalize(answer)))
    overlap = len(answer_terms & evidence_terms) / max(1, len(answer_terms))
    warnings: list[str] = []
    if module_id == "medicina" and any(marker in normalize(answer) for marker in ("diagnostico definitivo", "tome ", "prescrevo")):
        warnings.append("linguagem clínica incompatível com apoio informacional")
    if overlap < 0.08:
        return VerificationResult("repaired", max(0.2, overlap), ["alegações com baixa sustentação textual"], warnings)
    return VerificationResult("verified", min(0.99, 0.45 + overlap), [], warnings)
