from __future__ import annotations

from typing import Any

from ai.models import ContextModel
from ai.tools import tool_executor
from services.postgres_store import postgres_store


class ContextBuilder:
    def build(self, question: str, plan: dict) -> dict[str, Any]:
        tools = plan.get("tools", [])
        tools_output, tool_traces = tool_executor.execute_with_trace(plan=tools, question=question)

        problems = tools_output.get("zabbix.list_problems", {}).get("problems", [])
        containers = tools_output.get("docker.list_containers", {}).get("containers", [])
        host_count = tools_output.get("zabbix.count_hosts", {}).get("host_count", 0)
        modules = tools_output.get("registry.snapshot", {}).get("modules", [])
        insights = tools_output.get("learning.insights", {}) if isinstance(tools_output.get("learning.insights", {}), dict) else {}
        knowledge = tools_output.get("knowledge.search", {}).get("results", [])
        history = postgres_store.get_recent_messages(limit=8)
        temporal_groups_30d = postgres_store.get_group_trends(days=30, limit=10)

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
            "zabbix": {
                "host_count": host_count,
                "problem_count": len(problems) if isinstance(problems, list) else 0,
                "problem_summary": tools_output.get("zabbix.list_problems", {}).get("summary", {}),
            },
            "docker": {
                "container_count": len(containers) if isinstance(containers, list) else 0,
            },
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
            summary={
                "hosts": host_count,
                "problems": len(problems) if isinstance(problems, list) else 0,
                "containers": len(containers) if isinstance(containers, list) else 0,
                "modules": len(modules),
                "group_trends_30d": len(temporal_groups_30d),
            },
        )

        return context.model_dump()


context_builder = ContextBuilder()