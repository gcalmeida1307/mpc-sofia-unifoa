from __future__ import annotations

import re
import unicodedata
from typing import Any

from .domains import DOMAIN_CONTRACTS


def normalize(text: str) -> str:
    """Normalize accents and case for intent matching without changing evidence."""
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(char)
    )


SLEEP_MARKERS = (
    "piscada de sono",
    "piscadas de sono",
    "microssono",
    "micro sono",
    "sono durante o dia",
    "sonolencia diurna",
    "sonolencia durante o dia",
    "dormir pouco",
    "dormindo pouco",
    "sono insuficiente",
    "adormecer durante o dia",
    "ataque de sono",
    "trechos de sono",
)


def is_medical_sleep_query(question: str) -> bool:
    normalized = normalize(question)
    return any(marker in normalized for marker in SLEEP_MARKERS) or (
        any(term in normalized for term in ("sonolencia", "sono", "dormir", "adormecer"))
        and any(term in normalized for term in ("dia", "horas", "irritacao", "irritabilidade", "segundos", "5 horas"))
    )


MODULE_NAMES = {module_id: contract.name for module_id, contract in DOMAIN_CONTRACTS.items()}
MODULE_SCOPE_TERMS = {
    module_id: contract.keywords for module_id, contract in DOMAIN_CONTRACTS.items()
}

GENERIC_ANALYSIS_TERMS = (
    "resumo",
    "resuma",
    "conteudo",
    "conteúdo",
    "ponto",
    "pontos",
    "positivo",
    "positivos",
    "negativo",
    "negativos",
    "aspecto",
    "aspectos",
    "abordad",
    "analise",
    "análise",
    "vantagem",
    "desvantagem",
)


DIRECT_CONVERSATION_MARKERS = (
    "oi",
    "ola",
    "olá",
    "bom dia",
    "boa tarde",
    "boa noite",
    "obrigado",
    "obrigada",
    "quem e voce",
    "quem é você",
    "como voce pode ajudar",
    "como você pode ajudar",
)

DIRECT_WRITING_MARKERS = (
    "escreva",
    "redija",
    "reescreva",
    "reformule",
    "melhore este texto",
    "melhore esse texto",
    "corrija este texto",
    "corrija esse texto",
    "crie um email",
    "crie um e-mail",
    "escreva um email",
    "escreva um e-mail",
    "crie uma mensagem",
    "escreva uma mensagem",
    "traduza",
)

EVIDENCE_REQUEST_MARKERS = (
    "arquivo",
    "documento",
    "documentos",
    "fonte",
    "fontes",
    "link",
    "links",
    "base local",
    "base de conhecimento",
    "segundo",
    "conforme",
    "de acordo com",
    "no acordo",
    "na lei",
    "no contrato",
    "na imagem",
    "no csv",
    "no xlsx",
    "compare",
    "comparar",
    "jurisprudencia",
    "jurisprudência",
    "resuma",
    "resumo",
    "listar documentos",
    "o que temos sobre",
)


def route_query(module_id: str, question: str) -> dict[str, Any]:
    """Choose the smallest safe intelligence route for a user request."""

    del module_id
    normalized = normalize(question).strip()
    compact = re.sub(r"[!?.,;:]+", " ", normalized)
    compact = re.sub(r"\s+", " ", compact).strip()
    words = compact.split()

    if (
        any(compact == marker or compact.startswith(f"{marker} ") for marker in DIRECT_CONVERSATION_MARKERS)
        or (len(words) <= 5 and any(compact.startswith(marker) for marker in ("oi ", "ola ", "olá ")))
    ):
        return {
            "route": "conversation",
            "retrieval_required": False,
            "response_mode": "conversational",
            "reason": "saudação ou conversa sem pedido de evidência interna",
        }

    if any(marker in compact for marker in DIRECT_WRITING_MARKERS) and not any(marker in compact for marker in EVIDENCE_REQUEST_MARKERS):
        return {
            "route": "writing",
            "retrieval_required": False,
            "response_mode": "conversational",
            "reason": "tarefa de escrita sem exigência explícita de fonte interna",
        }

    if any(marker in compact for marker in EVIDENCE_REQUEST_MARKERS):
        return {
            "route": "evidence",
            "retrieval_required": True,
            "response_mode": "evidence",
            "reason": "a pergunta referencia conhecimento, documento ou fonte verificável",
        }

    if any(
        compact.startswith(marker)
        for marker in (
            "o que e ",
            "o que é ",
            "qual a diferenca",
            "qual é a diferença",
            "explique ",
            "como funciona",
            "como fazer",
            "por que ",
            "porque ",
        )
    ):
        return {
            "route": "explanation",
            "retrieval_required": True,
            "response_mode": "conversational",
            "reason": "explicação: consulta local primeiro, síntese humana depois",
        }

    return {
        "route": "evidence",
        "retrieval_required": True,
        "response_mode": "evidence",
        "reason": "pergunta de domínio: evidência local é a primeira autoridade",
    }


def _with_route(profile: dict[str, Any], module_id: str, question: str) -> dict[str, Any]:
    enriched = dict(profile)
    enriched.update(route_query(module_id, question))
    return enriched


def assess_module_scope(module_id: str, question: str) -> dict[str, Any]:
    """Explain whether a question appears aligned with the active module."""
    normalized = normalize(question)
    scores: dict[str, tuple[int, list[str]]] = {}
    for candidate, terms in MODULE_SCOPE_TERMS.items():
        matched = [term for term in terms if normalize(term) in normalized]
        if matched:
            scores[candidate] = (len(matched), matched[:4])
    current_score, current_terms = scores.get(module_id, (0, []))
    other_scores = [(score, candidate, terms) for candidate, (score, terms) in scores.items() if candidate != module_id]
    other_scores.sort(reverse=True)
    best_other = other_scores[0] if other_scores else (0, "", [])
    if current_score > 0 and current_score >= best_other[0]:
        status = "aligned"
        confidence = "high" if current_score >= 2 else "medium"
        related_module = module_id
    elif best_other[0] > 0 and not (
        best_other[0] == 1 and any(term in normalized for term in GENERIC_ANALYSIS_TERMS)
    ):
        status = "outside"
        confidence = "medium"
        related_module = best_other[1]
        current_terms = best_other[2]
    else:
        status = "uncertain"
        confidence = "low"
        related_module = module_id
    return {
        "status": status,
        "confidence": confidence,
        "module_id": module_id,
        "module_name": MODULE_NAMES.get(module_id, module_id),
        "related_module_id": related_module,
        "related_module_name": MODULE_NAMES.get(related_module, related_module),
        "matched_terms": current_terms,
    }


def classify_query(module_id: str, question: str) -> dict[str, Any]:
    """Return a privacy-safe semantic label used by retrieval and analytics.

    This is intentionally a small, explainable taxonomy. It routes a query to
    the right evidence profile; it never generates medical or legal conclusions.
    """
    normalized = normalize(question)
    tokens = set(re.findall(r"[\w]+", normalized))

    if module_id == "medicina" and is_medical_sleep_query(question):
        return _with_route({
            "intent": "clinical_symptom_assessment",
            "theme": "Sono e sonolência",
            "concepts": [
                "sonolência diurna",
                "microssono",
                "privação de sono",
                "sono insuficiente",
            ],
            "risk_flags": ["acidente_por_sonolencia"],
            "source_profile": "clinical_guideline",
        }, module_id, question)

    if module_id == "medicina":
        if any(term in normalized for term in ("sintoma", "dor", "febre", "tosse", "gripe", "influenza")):
            return _with_route({
                "intent": "clinical_symptom_assessment",
                "theme": "Sintomas e avaliação clínica",
                "concepts": ["sintomas", "avaliação clínica"],
                "risk_flags": ["avaliacao_profissional"],
                "source_profile": "clinical_guideline",
            }, module_id, question)
        if any(term in normalized for term in ("paciente", "prontuario", "fhir", "exame", "tratamento")):
            return _with_route({
                "intent": "clinical_record_or_protocol",
                "theme": "Protocolos e registros clínicos",
                "concepts": ["protocolo", "registro clínico", "FHIR"],
                "risk_flags": ["dados_de_saude"],
                "source_profile": "clinical_guideline",
            }, module_id, question)
        return _with_route({
            "intent": "medical_knowledge_lookup",
            "theme": "Conhecimento médico",
            "concepts": sorted(tokens)[:8],
            "risk_flags": ["avaliacao_profissional"],
            "source_profile": "clinical_guideline",
        }, module_id, question)

    if module_id in {"direito", "departamento-pessoal"}:
        if any(term in normalized for term in ("hora extra", "horas extras", "jornada", "hora negativa", "banco de horas")):
            theme = "Jornada, horas extras e compensação"
        elif any(term in normalized for term in ("acordo coletivo", "convencao coletiva", "saae")):
            theme = "Acordo coletivo e interpretação"
        elif any(term in normalized for term in ("ferias", "salario", "decimo terceiro", "13")):
            theme = "Direitos trabalhistas e remuneração"
        else:
            theme = "Legislação e documentos"
        return _with_route({
            "intent": "legal_document_analysis",
            "theme": theme,
            "concepts": sorted(tokens)[:8],
            "risk_flags": ["revisao_juridica"],
            "source_profile": "legal_primary_source",
        }, module_id, question)

    if module_id == "infraestrutura":
        if any(term in normalized for term in ("zabbix", "host", "monitoramento", "agent")):
            theme = "Zabbix e monitoramento"
        elif any(term in normalized for term in ("rede", "scan", "scanner", "snmp", "tcp", "udp")):
            theme = "Redes e diagnóstico"
        elif any(term in normalized for term in ("sistema operacional", "linux", "windows", "servidor")):
            theme = "Sistemas e disponibilidade"
        else:
            theme = "Infraestrutura e operações"
        return _with_route({
            "intent": "technical_procedure_or_diagnosis",
            "theme": theme,
            "concepts": sorted(tokens)[:8],
            "risk_flags": [],
            "source_profile": "technical_documentation",
        }, module_id, question)

    return _with_route({
        "intent": "module_knowledge_lookup",
        "theme": "Outros temas do módulo",
        "concepts": sorted(tokens)[:8],
        "risk_flags": [],
        "source_profile": "module_document",
    }, module_id, question)
