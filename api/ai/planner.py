from __future__ import annotations

from ai.models import PlanModel
from ai.planner_policy import planner_policy
from core.capability_resolver import capability_resolver
from semantic.fallback import deterministic_interpret
from semantic.models import SemanticQuery


INTENT_CAPABILITIES: dict[str, list[str]] = {
    "host_count": ["host_count"],
    "knowledge_lookup": ["knowledge_lookup", "host_analysis"],
    "active_trigger_summary": ["mcp_zabbix_summary"],
    "historical_trigger_summary": ["mcp_zabbix_summary"],
    "network_investigation": ["network_investigation", "incident_analysis"],
    "security_investigation": ["security_investigation", "knowledge_lookup"],
    "capacity_investigation": ["capacity_investigation", "incident_analysis"],
    "incident_analysis": ["incident_analysis"],
    "docker_action": ["docker_restart"],
    "docker_observe": ["docker_observe"],
    "marketplace": ["marketplace_browse"],
    "workflow_lookup": ["workflow_lookup"],
}


def build_plan(question: str, semantic_query: SemanticQuery | dict | None = None) -> dict:
    semantic = semantic_query or deterministic_interpret(question)
    if isinstance(semantic, dict):
        semantic = SemanticQuery.model_validate(semantic)

    capabilities = planner_policy.rank_capabilities(INTENT_CAPABILITIES.get(semantic.intent, []))
    tools = capability_resolver.resolve(intent=semantic.intent, requested_capabilities=capabilities)
    plan = PlanModel(
        intent=semantic.intent,
        domain=semantic.domain,
        capabilities=capabilities,
        tools=tools,
        semantic_query=semantic.model_dump(mode="json"),
        needs_llm_reasoning=True,
    )
    return plan.model_dump()
