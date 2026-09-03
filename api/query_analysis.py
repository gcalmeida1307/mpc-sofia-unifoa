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
        return {
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
        }

    if module_id == "medicina":
        if any(term in normalized for term in ("sintoma", "dor", "febre", "tosse", "gripe", "influenza")):
            return {
                "intent": "clinical_symptom_assessment",
                "theme": "Sintomas e avaliação clínica",
                "concepts": ["sintomas", "avaliação clínica"],
                "risk_flags": ["avaliacao_profissional"],
                "source_profile": "clinical_guideline",
            }
        if any(term in normalized for term in ("paciente", "prontuario", "fhir", "exame", "tratamento")):
            return {
                "intent": "clinical_record_or_protocol",
                "theme": "Protocolos e registros clínicos",
                "concepts": ["protocolo", "registro clínico", "FHIR"],
                "risk_flags": ["dados_de_saude"],
                "source_profile": "clinical_guideline",
            }
        return {
            "intent": "medical_knowledge_lookup",
            "theme": "Conhecimento médico",
            "concepts": sorted(tokens)[:8],
            "risk_flags": ["avaliacao_profissional"],
            "source_profile": "clinical_guideline",
        }

    if module_id in {"direito", "departamento-pessoal"}:
        if any(term in normalized for term in ("hora extra", "horas extras", "jornada", "hora negativa", "banco de horas")):
            theme = "Jornada, horas extras e compensação"
        elif any(term in normalized for term in ("acordo coletivo", "convencao coletiva", "saae")):
            theme = "Acordo coletivo e interpretação"
        elif any(term in normalized for term in ("ferias", "salario", "decimo terceiro", "13")):
            theme = "Direitos trabalhistas e remuneração"
        else:
            theme = "Legislação e documentos"
        return {
            "intent": "legal_document_analysis",
            "theme": theme,
            "concepts": sorted(tokens)[:8],
            "risk_flags": ["revisao_juridica"],
            "source_profile": "legal_primary_source",
        }

    if module_id == "infraestrutura":
        if any(term in normalized for term in ("zabbix", "host", "monitoramento", "agent")):
            theme = "Zabbix e monitoramento"
        elif any(term in normalized for term in ("rede", "scan", "scanner", "snmp", "tcp", "udp")):
            theme = "Redes e diagnóstico"
        elif any(term in normalized for term in ("sistema operacional", "linux", "windows", "servidor")):
            theme = "Sistemas e disponibilidade"
        else:
            theme = "Infraestrutura e operações"
        return {
            "intent": "technical_procedure_or_diagnosis",
            "theme": theme,
            "concepts": sorted(tokens)[:8],
            "risk_flags": [],
            "source_profile": "technical_documentation",
        }

    return {
        "intent": "module_knowledge_lookup",
        "theme": "Outros temas do módulo",
        "concepts": sorted(tokens)[:8],
        "risk_flags": [],
        "source_profile": "module_document",
    }
