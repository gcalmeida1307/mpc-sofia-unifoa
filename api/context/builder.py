from __future__ import annotations

from typing import Any

from ai.models import ContextModel
from ai.tools import tool_executor
from services.postgres_store import postgres_store
from core.domain_intelligence import domain_provider_registry


class ContextBuilder:
    def build(self, question: str, plan: dict, agent: dict[str, Any] | None = None, hypothesis: dict[str, Any] | None = None) -> dict[str, Any]:
        tools = plan.get("tools", [])
        tools_output, tool_traces = tool_executor.execute_with_trace(plan=tools, question=question)
        domain_id = str(plan.get("domain_id") or "infrastructure")
        domain_context = domain_provider_registry.context(domain_id, tools_output)

        problems = domain_context.get("evidence", [])
        metrics = domain_context.get("metrics", {})
        containers: list = []
        host_count = int(metrics.get("entities", domain_context.get("scope", {}).get("host_count", 0)) or 0)
        active_problem_count = len(problems) if isinstance(problems, list) else 0
        problem_summary = metrics
        modules = tools_output.get("registry.snapshot", {}).get("modules", [])
        insights = tools_output.get("learning.insights", {}) if isinstance(tools_output.get("learning.insights", {}), dict) else {}
        knowledge = tools_output.get("knowledge.search", {}).get("results", [])
        history = postgres_store.get_recent_messages(limit=8)
        # Deep investigations already carry scoped live evidence. The historical
        # cross-snapshot aggregation is expensive and unrelated to the immediate
        # trigger → item → history chain.
        temporal_groups_30d = [] if plan.get("intent") == "incident_analysis" else postgres_store.get_group_trends(days=30, limit=10)

        risk_level = "low"
        if isinstance(problems, list) and len(problems) >= 30:
            risk_level = "high"
        elif isinstance(problems, list) and len(problems) > 0:
            risk_level = "medium"

        risks = [
            {
                "name": "active_problems",
                "level": risk_level,
                "value": len(problems) if isinstance(problems, list) else 0,
                "mitigation": "Priorizar severidades mais altas e validar runbook antes de acao destrutiva.",
            }
        ]

        snapshot = {
            "domain": {"domain_id": domain_id, "entity_count": host_count,
                       "event_count": active_problem_count, "metrics": problem_summary},
            "registry": {
                "modules": modules,
            },
            "temporal": {
                "group_trends_30d": temporal_groups_30d,
            },
        }

        context = ContextModel(
            question=question,
            intent=plan.get("intent", "unknown"),
            plan=plan,
            snapshot=snapshot,
            knowledge=knowledge if isinstance(knowledge, list) else [],
            insights=insights.get("patterns", []) if isinstance(insights.get("patterns", []), list) else [],
            history=history,
            evidence=tool_traces,
            risks=risks,
            tools=tools_output,
            agent=agent or {},
            hypothesis=hypothesis or {},
            summary={
                "entities": host_count,
                "events": active_problem_count,
                "modules": len(modules),
                "group_trends_30d": len(temporal_groups_30d),
            },
        )
        result = context.model_dump()
        result["domain"] = domain_context
        result["domain_id"] = domain_id
        return result


context_builder = ContextBuilder()
