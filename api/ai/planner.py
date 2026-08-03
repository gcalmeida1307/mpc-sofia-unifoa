from __future__ import annotations

from ai.models import PlanModel
from core.capability_resolver import capability_resolver


def _looks_like_host_count(question: str) -> bool:
    q = question.lower()
    count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
    host_terms = ["host", "hosts"]
    severity_terms = ["severity", "severidade", "average", "avg", "avarege", "avarage"]
    return any(term in q for term in count_terms) and any(term in q for term in host_terms) and not any(term in q for term in severity_terms)


def _infer_intent_and_capabilities(question: str) -> tuple[str, list[str]]:
    q = question.lower()

    if _looks_like_host_count(question):
        return "host_count", ["host_count"]

    if any(term in q for term in ["quais hosts", "mais problema", "incidente", "indispon", "link down", "alerta"]):
        return "incident_analysis", ["host_analysis", "incident_analysis"]

    if any(term in q for term in ["host", "hosts", "zabbix", "severity", "severidade", "grupo", "problema"]):
        return "host_analysis", ["host_analysis"]

    if any(term in q for term in ["reinicie", "reiniciar", "restart", "suba", "start"]):
        return "docker_action", ["docker_restart"]

    if any(term in q for term in ["docker", "container", "containers"]):
        return "docker_observe", ["docker_observe"]

    if any(term in q for term in ["marketplace", "marktplace", "market place", "modulo", "módulo"]):
        return "marketplace", ["marketplace_browse"]

    if any(term in q for term in ["knowledge", "runbook", "documentacao", "documentação", "doc"]):
        return "knowledge_lookup", ["knowledge_lookup"]

    if any(term in q for term in ["n8n", "workflow", "automacao", "automação"]):
        return "workflow_lookup", ["workflow_lookup"]

    return "general_chat", []


def build_plan(question: str) -> dict:
    intent, capabilities = _infer_intent_and_capabilities(question)
    tools = capability_resolver.resolve(intent=intent, requested_capabilities=capabilities)

    plan = PlanModel(
        intent=intent,
        capabilities=capabilities,
        tools=tools,
        needs_llm_reasoning=True,
    )
    return plan.model_dump()
