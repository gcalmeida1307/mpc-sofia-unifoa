from __future__ import annotations

from typing import Any


class CriticEngine:
    def evaluate(self, question: str, plan: dict[str, Any], context: dict[str, Any], answer: str) -> dict[str, Any]:
        issues: list[str] = []
        revised_answer: str | None = None

        if not answer or not answer.strip():
            issues.append("Resposta vazia")

        q = question.lower()
        if self._looks_like_host_count(q):
            expected = str(context.get("summary", {}).get("hosts", 0))
            if expected not in answer:
                issues.append("Resposta de contagem de hosts sem o total esperado")
                revised_answer = f"Voce possui {expected} host(s) cadastrados no Zabbix."

        if plan.get("tools") and len(answer) > 1800:
            issues.append("Resposta operacional excessivamente longa")

        if "acessar" in answer.lower() and "diretamente" in answer.lower() and "zabbix" in answer.lower():
            issues.append("Resposta pode violar separacao Core/Conector")

        approved = len(issues) == 0
        score = 1.0 if approved else max(0.35, 1.0 - (0.2 * len(issues)))
        confidence = round(score, 2)
        if plan.get("intent") == "general_chat" and not plan.get("tools"):
            confidence = min(confidence, 0.7)

        return {
            "approved": approved,
            "score": confidence,
            "confidence": confidence,
            "issues": issues,
            "revised_answer": revised_answer,
            "rationale": "Validacao concluida com base em consistencia de evidencias e politicas de risco.",
        }

    @staticmethod
    def _looks_like_host_count(question: str) -> bool:
        count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
        host_terms = ["host", "hosts"]
        severity_terms = ["severity", "severidade", "average", "avg", "avarege", "avarage"]
        return any(term in question for term in count_terms) and any(term in question for term in host_terms) and not any(term in question for term in severity_terms)


critic_engine = CriticEngine()
