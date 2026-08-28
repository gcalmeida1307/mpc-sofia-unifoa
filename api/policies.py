from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModulePolicy:
    allow_general_knowledge: bool
    high_risk: bool
    min_evidence_score: float
    require_citation: bool


POLICIES = {
    "medicina": ModulePolicy(False, True, 0.38, True),
    "infraestrutura": ModulePolicy(True, False, 0.28, False),
    "gestao-empresarial": ModulePolicy(True, False, 0.25, False),
    "almoxarifado": ModulePolicy(True, False, 0.25, False),
}


def policy_for(module_id: str) -> ModulePolicy:
    return POLICIES.get(module_id, ModulePolicy(False, False, 0.35, True))


def expand_query(module_id: str, query: str) -> str:
    expansions = {
        "gripe": "influenza sintomas febre tosse J09 J10 J11",
        "resfriado": "rinofaringite coriza sintomas",
        "pressao": "hipertensao hipotensao arterial",
        "dor de cabeca": "cefaleia enxaqueca",
    }
    normalized = query.casefold()
    extra = " ".join(value for key, value in expansions.items() if key in normalized)
    return f"{query} {extra}".strip()
