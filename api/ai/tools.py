from __future__ import annotations

from context.infrastructure import infrastructure_provider
from context.learning import learning_provider
from context.knowledge import knowledge_provider
from context.registry import registry_provider
from services.marketplace import get_marketplace_catalog
from services.workflows import list_n8n_templates


class ToolExecutor:
    def execute(self, plan: list[str], question: str) -> dict:
        output = {}
        for tool_name in plan:
            output[tool_name] = self._run_tool(tool_name, question)
        return output

    def _run_tool(self, tool_name: str, question: str) -> dict:
        if tool_name in {"zabbix.count_hosts", "zabbix.list_problems", "docker.list_containers", "docker.restart_container"}:
            return infrastructure_provider.execute(tool_name, question)

        if tool_name == "marketplace.catalog":
            return get_marketplace_catalog()

        if tool_name == "knowledge.search":
            return knowledge_provider.execute(tool_name, question)

        if tool_name == "workflow.templates":
            return list_n8n_templates()

        if tool_name == "learning.insights":
            return learning_provider.execute(tool_name, question)

        if tool_name == "registry.snapshot":
            return registry_provider.execute(tool_name, question)

        return {"error": f"tool {tool_name} not implemented"}


tool_executor = ToolExecutor()
