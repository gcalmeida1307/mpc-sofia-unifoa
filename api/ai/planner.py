from __future__ import annotations

from ai.models import PlanModel
from ai.planner_policy import planner_policy
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

    trigger_terms = ["trigger", "triggers", "alerta ativo", "problema ativo"]
    if any(term in q for term in trigger_terms):
        return "active_trigger_summary", ["mcp_zabbix_summary"]

    documentation_terms = ["runbook", "documentacao", "documenta\u00e7\u00e3o", "doc", "base", "procedimento", "como investigar"]
    zabbix_terms = ["zabbix", "host", "hosts", "problema", "alerta", "trigger", "severidade", "severity"]
    if any(term in q for term in documentation_terms) and any(term in q for term in zabbix_terms):
        return "knowledge_lookup", ["knowledge_lookup", "host_analysis"]

    if any(term in q for term in ["switch", "stp", "crc", "broadcast storm", "storm", "lent", "lento"]):
        return "network_investigation", ["network_investigation", "incident_analysis"]

    if any(term in q for term in ["vpn", "firewall", "auth", "login", "security", "seguranca", "ataque"]):
        return "security_investigation", ["security_investigation", "knowledge_lookup"]

    if any(term in q for term in ["cpu", "memory", "ram", "disk", "storage", "latency", "capacity"]):
        return "capacity_investigation", ["capacity_investigation", "incident_analysis"]

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
    ranked_capabilities = planner_policy.rank_capabilities(capabilities)
    tools = capability_resolver.resolve(intent=intent, requested_capabilities=ranked_capabilities)

    plan = PlanModel(
        intent=intent,
        capabilities=ranked_capabilities,
        tools=tools,
        needs_llm_reasoning=True,
    )
    return plan.model_dump()
