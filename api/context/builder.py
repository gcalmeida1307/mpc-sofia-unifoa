from __future__ import annotations

from typing import Any

from ai.tools import tool_executor


class ContextBuilder:
    def build(self, question: str, plan: dict) -> dict[str, Any]:
        tools = plan.get("tools", [])
        tools_output = tool_executor.execute(plan=tools, question=question)

        problems = tools_output.get("zabbix.list_problems", {}).get("problems", [])
        containers = tools_output.get("docker.list_containers", {}).get("containers", [])
        host_count = tools_output.get("zabbix.count_hosts", {}).get("host_count", 0)
        modules = tools_output.get("registry.snapshot", {}).get("modules", [])
        insights = tools_output.get("learning.insights", {})

        return {
            "summary": {
                "hosts": host_count,
                "problems": len(problems),
                "containers": len(containers) if isinstance(containers, list) else 0,
                "modules": len(modules),
            },
            "question": question,
            "plan": plan,
            "tools": tools_output,
            "insights": insights,
        }


context_builder = ContextBuilder()