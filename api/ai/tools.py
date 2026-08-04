from __future__ import annotations

import json
from time import perf_counter

from context.infrastructure import infrastructure_provider
from context.learning import learning_provider
from context.knowledge import knowledge_provider
from context.registry import registry_provider
from services.mcp_server import mcp_server
from services.postgres_store import postgres_store
from services.marketplace import get_marketplace_catalog
from services.workflows import list_n8n_templates


class ToolExecutor:
    def execute(self, plan: list[str], question: str) -> dict:
        output, _ = self.execute_with_trace(plan=plan, question=question)
        return output

    def execute_with_trace(self, plan: list[str], question: str) -> tuple[dict, list[dict]]:
        output = {}
        traces: list[dict] = []
        for tool_name in plan:
            start = perf_counter()
            result = self._run_tool(tool_name, question)
            duration = round(perf_counter() - start, 4)
            success = not isinstance(result, dict) or "error" not in result
            trace = {
                "tool": tool_name,
                "success": success,
                "duration": duration,
                "evidence": self._extract_evidence(tool_name, result),
                "rollback": self._rollback_hint(tool_name),
            }
            traces.append(trace)
            output[tool_name] = result
        postgres_store.save_tool_audit(traces=traces, metadata={"question": question})
        return output, traces

    def _run_tool(self, tool_name: str, question: str) -> dict:
        if tool_name.startswith("mcp."):
            return self._run_mcp_tool(tool_name.removeprefix("mcp."))

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

    @staticmethod
    def _run_mcp_tool(name: str) -> dict:
        response = mcp_server.handle(
            {
                "jsonrpc": "2.0",
                "id": "sofia-internal",
                "method": "tools/call",
                "params": {"name": name, "arguments": {}},
            }
        )
        result = (response or {}).get("result", {}) if isinstance(response, dict) else {}
        content = result.get("content", []) if isinstance(result, dict) else []
        if not content or not isinstance(content[0], dict):
            return {"error": f"MCP tool returned no content: {name}"}
        if result.get("isError"):
            return {"error": str(content[0].get("text", "MCP tool failed"))}
        try:
            parsed = json.loads(str(content[0].get("text", "{}")))
        except json.JSONDecodeError:
            return {"error": f"MCP tool returned invalid JSON: {name}"}
        return parsed if isinstance(parsed, dict) else {"result": parsed}

    def _extract_evidence(self, tool_name: str, result: dict) -> list[str]:
        if not isinstance(result, dict):
            return [f"{tool_name}: resposta nao estruturada"]
        if "error" in result:
            return [f"{tool_name}: erro={result.get('error')}"]

        evidence: list[str] = []
        if tool_name == "zabbix.count_hosts":
            evidence.append(f"hosts={result.get('host_count', 0)}")
        if tool_name == "zabbix.list_problems":
            problems = result.get("problems", [])
            evidence.append(f"problems={len(problems) if isinstance(problems, list) else 0}")
        if tool_name == "docker.list_containers":
            evidence.append(f"containers={result.get('container_count', 0)}")
        if tool_name == "knowledge.search":
            hits = result.get("results", [])
            evidence.append(f"knowledge_hits={len(hits) if isinstance(hits, list) else 0}")
        if tool_name == "learning.insights":
            patterns = result.get("patterns", [])
            evidence.append(f"patterns={len(patterns) if isinstance(patterns, list) else 0}")
        if tool_name == "registry.snapshot":
            evidence.append(f"modules={len(result.get('modules', []))}")

        return evidence or [f"{tool_name}: executed"]

    @staticmethod
    def _rollback_hint(tool_name: str) -> str | None:
        if tool_name == "docker.restart_container":
            return "Validar healthcheck do container e executar rollback de imagem se necessario"
        return None


tool_executor = ToolExecutor()
