"""Small, auditable Root Cause Analysis contract for SOFIA.

RCA is deliberately evidence-first.  It can organize facts, hypotheses and
next tests, but it cannot promote a correlation or a source assertion into a
proven causal explanation.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from .query_analysis import normalize


@dataclass(frozen=True)
class RCAReport:
    problem: str
    facts: tuple[dict[str, Any], ...] = ()
    candidate_causes: tuple[dict[str, Any], ...] = ()
    relationships: tuple[dict[str, Any], ...] = ()
    unknowns: tuple[str, ...] = ()
    next_tests: tuple[str, ...] = ()
    confidence: str = "preliminar"

    def public_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_rca_request(question: str) -> bool:
    normalized = normalize(question)
    return any(
        marker in normalized
        for marker in (
            "rca",
            "root cause",
            "causa raiz",
            "causa-raiz",
            "causa do incidente",
            "por que falhou",
            "porque falhou",
            "analise do incidente",
            "analisar o incidente",
        )
    )


def _clip(value: str, limit: int = 420) -> str:
    value = re.sub(r"\s+", " ", value).strip(" -•\t")
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def build_report(question: str, result: Any) -> RCAReport:
    facts: list[dict[str, Any]] = []
    for index, item in enumerate(result.evidence[:6], 1):
        locator = item.chunk.locator or (f"página {item.chunk.page}" if item.chunk.page else f"trecho {item.chunk.ordinal}")
        facts.append(
            {
                "id": f"F{index}",
                "kind": "fact",
                "statement": _clip(item.chunk.text),
                "source": item.chunk.path.name,
                "locator": locator,
                "evidence_score": round(float(item.score), 4),
            }
        )

    candidate_causes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    from .relational_reasoning import analyze

    analysis = analyze(result)
    for relation in analysis.get("relations", []):
        kind = str(relation.get("kind", ""))
        if kind not in {"causal_claim", "hypothesis", "correlation"}:
            continue
        entry = {
            "statement": _clip(str(relation.get("quote") or f"{relation.get('from')} → {relation.get('to')}")),
            "kind": "source_claim" if kind == "causal_claim" else kind,
            "status": "não comprovada independentemente",
            "premises": list(relation.get("premises", [])),
            "source": relation.get("source", ""),
        }
        if kind in {"causal_claim", "hypothesis"}:
            candidate_causes.append(entry)
        else:
            relationships.append(entry)

    for conflict in result.conflicts:
        relationships.append(
            {
                "kind": "conflict",
                "status": "requer validação de versão, escopo ou data",
                "statement": f"Possível tensão entre {conflict.get('left_source', '?')} e {conflict.get('right_source', '?')}.",
            }
        )

    unknowns = [
        "A evidência recuperada não demonstra, sozinha, uma causa raiz.",
        "Faltam cronologia do evento, impacto mensurado e teste de confirmação ou eliminação das hipóteses.",
    ]
    if candidate_causes:
        unknowns.append("As causas candidatas são alegações ou hipóteses presentes nas fontes; ainda não foram validadas como causalidade.")
    next_tests = (
        "Fixar a linha do tempo: o que ocorreu, quando, onde e qual foi o impacto.",
        "Separar sintoma, fato observado e causa candidata; coletar a evidência que possa confirmar ou refutar cada hipótese.",
        "Reexecutar ou comparar o cenário controladamente antes de atribuir causalidade.",
    )
    return RCAReport(
        problem=question.strip(),
        facts=tuple(facts),
        candidate_causes=tuple(candidate_causes),
        relationships=tuple(relationships),
        unknowns=tuple(unknowns),
        next_tests=next_tests,
    )


def render_report(question: str, result: Any, language: str = "pt-BR") -> str | None:
    if language != "pt-BR" or not is_rca_request(question) or not result.has_quality_evidence:
        return None
    report = build_report(question, result)
    lines = [
        "RCA preliminar",
        "Organizei o que os documentos permitem afirmar, sem transformar correlação ou hipótese em causa raiz comprovada.",
        "",
        "Fatos observados",
    ]
    lines.extend(f"- [{item['id']}] {item['statement']}" for item in report.facts)
    lines.append("")
    lines.append("Causas candidatas")
    if report.candidate_causes:
        lines.extend(f"- {item['statement']} — {item['kind']}; {item['status']}." for item in report.candidate_causes[:4])
    else:
        lines.append("- Nenhuma causa raiz foi demonstrada pelos trechos recuperados.")
    lines.append("")
    lines.append("Relações, correlações e conflitos")
    if report.relationships:
        lines.extend(f"- {item['statement']} — {item.get('status', 'relação documentada')}." for item in report.relationships[:4])
    else:
        lines.append("- Não foi identificada uma relação causal comprovada nesta consulta.")
    lines.append("")
    lines.append("Lacunas")
    lines.extend(f"- {item}" for item in report.unknowns)
    lines.append("")
    lines.append("Próximos testes")
    lines.extend(f"- {item}" for item in report.next_tests)
    return "\n".join(lines)
