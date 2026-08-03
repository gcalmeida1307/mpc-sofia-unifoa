from __future__ import annotations

from typing import Any


class ReasoningEngine:
    def build(self, question: str, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        tools = plan.get("tools", []) if isinstance(plan, dict) else []
        summary = context.get("summary", {}) if isinstance(context, dict) else {}
        operational = bool(tools)
        risks = context.get("risks", []) if isinstance(context, dict) else []
        selected_hypothesis = context.get("hypothesis", {}).get("selected_hypothesis") if isinstance(context, dict) else None

        objective = "Responder a pergunta com base no contexto consolidado do SOFIA."
        if operational:
            objective = "Responder com evidencias operacionais e recomendacao acionavel."

        deterministic_answer = None
        q = question.lower()
        if self._looks_like_host_count(q):
            host_count = summary.get("hosts", 0)
            deterministic_answer = f"Voce possui {host_count} host(s) cadastrados no Zabbix."

        recommended_actions = self._recommended_actions(summary=summary, risks=risks, operational=operational)
        if selected_hypothesis:
            recommended_actions.insert(0, f"Validar a hipotese prioritaria: {selected_hypothesis}.")
        justification = (
            "Plano baseado no snapshot mais recente, trilha de tools executadas e contexto do registry."
            if operational
            else "Plano baseado em conversa geral com fallback seguro quando faltar contexto operacional."
        )
        if selected_hypothesis:
            justification = f"{justification} Hipotese inicial selecionada para reduzir tempo de diagnostico."

        return {
            "objective": objective,
            "mode": "operational" if operational else "general",
            "selected_tools": tools,
            "context_summary": summary,
            "recommended_actions": recommended_actions,
            "justification": justification,
            "constraints": [
                "Usar o contexto do SOFIA como fonte para dados operacionais.",
                "Nao inventar dados externos.",
                "Ser objetivo e acionavel.",
            ],
            "deterministic_answer": deterministic_answer,
        }

    def to_developer_note(self, reasoning: dict[str, Any]) -> str:
        return (
            "Raciocinio estruturado do SOFIA:\n"
            f"- objetivo: {reasoning.get('objective', '')}\n"
            f"- modo: {reasoning.get('mode', '')}\n"
            f"- tools: {', '.join(reasoning.get('selected_tools', []))}\n"
            f"- resumo: {reasoning.get('context_summary', {})}\n"
            f"- recomendacoes: {reasoning.get('recommended_actions', [])}\n"
            "- restricoes: usar somente contexto operacional quando aplicavel e nao inventar evidencias."
        )

    @staticmethod
    def _recommended_actions(summary: dict[str, Any], risks: list[dict[str, Any]], operational: bool) -> list[str]:
        if not operational:
            return ["Se a pergunta envolver infraestrutura, executar tools operacionais antes da resposta final."]

        actions: list[str] = []
        problems = int(summary.get("problems", 0) or 0)
        if problems > 0:
            actions.append("Priorizar problemas por severidade e validar hosts mais reincidentes.")
            actions.append("Relacionar eventos ativos com runbooks encontrados no Knowledge.")
        if int(summary.get("containers", 0) or 0) == 0:
            actions.append("Confirmar se a telemetria Docker esta disponivel no ambiente atual.")
        if risks:
            actions.append("Aplicar confirmacao humana para acoes de risco medio ou alto.")
        if not actions:
            actions.append("Sem riscos operacionais relevantes no momento; manter monitoramento continuo.")
        return actions

    @staticmethod
    def _looks_like_host_count(question: str) -> bool:
        count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
        host_terms = ["host", "hosts"]
        severity_terms = ["severity", "severidade", "average", "avg", "avarege", "avarage"]
        return any(term in question for term in count_terms) and any(term in question for term in host_terms) and not any(term in question for term in severity_terms)


reasoning_engine = ReasoningEngine()
