from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .policies import ModulePolicy, policy_for
from .providers import Generation, generate_with_fallback
from .retrieval import RetrievalResult, retrieve


@dataclass(frozen=True)
class OrchestrationResult:
    answer: str
    provider: str
    model: str
    sources: list[str]
    evidence_score: float
    evidence_found: bool
    verified: bool


def _system(policy: ModulePolicy) -> str:
    risk = "Você está em um domínio de saúde: não diagnostique, não prescreva e sinalize urgência quando aplicável." if policy.high_risk else ""
    return f"Você é Sofia. Responda em português natural, claro e acolhedor. {risk} Cite somente fontes que realmente sustentem a resposta. Diferencie explicitamente fatos dos documentos, conhecimento geral e incerteza. Um documento apenas relacionado não é evidência suficiente."


def _prompt(question: str, result: RetrievalResult, policy: ModulePolicy) -> str:
    if result.has_quality_evidence:
        evidence = result.context
        instruction = "Use as evidências abaixo como base principal. Você pode complementar com conhecimento geral apenas se a política permitir e deve dizer quando fizer isso."
    elif policy.allow_general_knowledge:
        evidence = "Nenhuma evidência local passou pelo gate de qualidade."
        instruction = "Responda com conhecimento geral, deixando claro que os documentos locais não sustentaram a resposta."
    else:
        evidence = "Nenhuma evidência local passou pelo gate de qualidade."
        instruction = "Não responda como se houvesse evidência. Diga que não há informação suficiente nos documentos locais."
    return f"Pergunta: {question}\n\n{instruction}\n\nEVIDÊNCIA LOCAL:\n{evidence}"


def _verify(answer: str, result: RetrievalResult, policy: ModulePolicy) -> bool:
    if not answer.strip():
        return False
    if policy.high_risk and not result.has_quality_evidence and any(word in answer.casefold() for word in ("diagnóstico", "dose", "tratamento", "deve tomar")):
        return False
    if result.has_quality_evidence:
        answer_terms = {term for term in re.findall(r"[\w]+", answer.casefold()) if len(term) > 4}
        evidence_terms = {term for term in re.findall(r"[\w]+", result.context.casefold()) if len(term) > 4}
        return len(answer_terms & evidence_terms) >= 2
    return policy.allow_general_knowledge


def local_no_evidence(policy: ModulePolicy) -> str:
    if policy.high_risk:
        return "Não encontrei evidência suficiente nos documentos locais para responder com segurança. Consulte uma fonte médica confiável ou um profissional de saúde."
    return "Não encontrei evidência suficiente nos documentos locais para responder com segurança."


async def answer(*, root: Path, module_id: str, provider: str, question: str, history: list[dict[str, str]]) -> OrchestrationResult:
    policy = policy_for(module_id)
    result = retrieve(root, module_id, question, policy)
    if not result.has_quality_evidence and not policy.allow_general_knowledge:
        return OrchestrationResult(local_no_evidence(policy), "policy", "evidence-gate", list(result.sources), 0.0, False, True)
    try:
        generated: Generation = await generate_with_fallback(provider, _system(policy), _prompt(question, result, policy), history[-10:])
    except RuntimeError:
        if not result.has_quality_evidence:
            return OrchestrationResult(local_no_evidence(policy), "policy", "evidence-gate", list(result.sources), 0.0, False, True)
        return OrchestrationResult("Encontrei documentos relacionados, mas não foi possível gerar uma resposta confiável agora. Consulte as fontes exibidas e tente novamente com um provider disponível.", "error", "generation-failed", list(result.sources), max(item.score for item in result.evidence), True, False)
    verified = _verify(generated.answer, result, policy)
    if not verified:
        return OrchestrationResult("A resposta gerada não passou pela verificação de evidências. Não vou apresentá-la como fato; consulte as fontes e tente reformular a pergunta.", generated.provider, "verification-failed", list(result.sources), max(item.score for item in result.evidence) if result.evidence else 0.0, bool(result.evidence), False)
    return OrchestrationResult(generated.answer, generated.provider, generated.model, list(result.sources), max(item.score for item in result.evidence) if result.evidence else 0.0, bool(result.evidence), True)
