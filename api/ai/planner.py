from __future__ import annotations

from ai.models import PlanModel


def _looks_like_host_count(question: str) -> bool:
    q = question.lower()
    count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
    host_terms = ["host", "hosts"]
    severity_terms = ["severity", "severidade", "average", "avg", "avarege", "avarage"]
    return any(term in q for term in count_terms) and any(term in q for term in host_terms) and not any(term in q for term in severity_terms)


def _looks_like_operational_question(question: str) -> bool:
    q = question.lower()
    return any(
        term in q
        for term in [
            "zabbix",
            "host",
            "hosts",
            "docker",
            "container",
            "containers",
            "problem",
            "problema",
            "alerta",
            "alert",
            "severity",
            "severidade",
            "grupo",
            "marketplace",
            "workflow",
            "n8n",
            "knowledge",
            "runbook",
            "doc",
            "documentacao",
            "documentação",
            "route",
            "rotas",
        ]
    )


def build_plan(question: str) -> dict:
    q = question.lower()
    tools: list[str] = []
    operational_question = _looks_like_operational_question(question)

    if _looks_like_host_count(question):
        tools.append("zabbix.count_hosts")
    elif any(term in q for term in ["host", "hosts", "zabbix", "problema", "alerta", "severity", "severidade", "grupo"]):
        tools.append("zabbix.list_problems")
        tools.append("zabbix.count_hosts")

    if any(term in q for term in ["container", "containers", "docker"]):
        tools.append("docker.list_containers")

    if any(term in q for term in ["reinicie", "reiniciar", "restart", "suba", "start"]):
        tools.append("docker.list_containers")
        tools.append("docker.restart_container")

    if any(term in q for term in ["marketplace", "marktplace", "market place", "modulo", "módulo"]):
        tools.append("marketplace.catalog")

    if any(term in q for term in ["knowledge", "runbook", "documentacao", "documentação", "doc"]):
        tools.append("knowledge.search")

    if any(term in q for term in ["n8n", "workflow", "automacao", "automação"]):
        tools.append("workflow.templates")

    if operational_question:
        tools.append("registry.snapshot")
        tools.append("learning.insights")
    tools = sorted(set(tools))

    plan = PlanModel(
        intent="operational-assistant",
        tools=tools,
        needs_llm_reasoning=True,
    )
    return plan.model_dump()
