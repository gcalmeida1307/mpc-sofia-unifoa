from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from connectors.zabbix import ZabbixConnector
from core.registry import registry
from services.infrastructure import get_infrastructure_summary
from services.knowledge import search_knowledge

JSON_RPC_VERSION = "2.0"
SUPPORTED_PROTOCOL_VERSIONS = {"2024-11-05", "2025-03-26"}


@dataclass(frozen=True)
class McpTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], Any]


class McpServer:
    """Transport-agnostic MCP server with read-only SOFIA capabilities."""

    def __init__(self) -> None:
        self._tools = {
            "sofia.platform.status": McpTool(
                "sofia.platform.status",
                "Return SOFIA modules, services and registered capabilities.",
                {"type": "object", "properties": {}, "additionalProperties": False},
                self._platform_status,
            ),
            "sofia.infrastructure.summary": McpTool(
                "sofia.infrastructure.summary",
                "Return a local infrastructure summary collected by the SOFIA runtime.",
                {"type": "object", "properties": {}, "additionalProperties": False},
                lambda _: get_infrastructure_summary(),
            ),
            "sofia.knowledge.search": McpTool(
                "sofia.knowledge.search",
                "Search indexed runbooks, documentation and approved knowledge sources.",
                {
                    "type": "object",
                    "properties": {"query": {"type": "string", "minLength": 2, "maxLength": 500}},
                    "required": ["query"],
                    "additionalProperties": False,
                },
                lambda arguments: search_knowledge(arguments["query"]),
            ),
            "sofia.zabbix.active_summary": McpTool(
                "sofia.zabbix.active_summary",
                "Return current Zabbix host and active problem impact summary.",
                {"type": "object", "properties": {}, "additionalProperties": False},
                self._zabbix_active_summary,
            ),
        }

    def handle(self, payload: Any) -> dict[str, Any] | None:
        if not isinstance(payload, dict) or payload.get("jsonrpc") != JSON_RPC_VERSION:
            return self._error(None, -32600, "Invalid JSON-RPC request")

        request_id = payload.get("id")
        method = payload.get("method")
        if not isinstance(method, str):
            return self._error(request_id, -32600, "Missing method")
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return self._result(request_id, {})
        if method == "initialize":
            params = payload.get("params") or {}
            version = params.get("protocolVersion")
            selected = version if version in SUPPORTED_PROTOCOL_VERSIONS else "2025-03-26"
            return self._result(request_id, {
                "protocolVersion": selected,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "sofia-mcp", "version": "1.0.0"},
                "instructions": "SOFIA tools are read-only. Search approved knowledge before operational answers.",
            })
        if method == "tools/list":
            return self._result(request_id, {"tools": [self._descriptor(tool) for tool in self._tools.values()]})
        if method == "tools/call":
            return self._call_tool(request_id, payload.get("params") or {})
        return self._error(request_id, -32601, f"Method not found: {method}")

    def _call_tool(self, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str) or name not in self._tools:
            return self._error(request_id, -32602, "Unknown tool")
        if not isinstance(arguments, dict):
            return self._error(request_id, -32602, "Tool arguments must be an object")
        tool = self._tools[name]
        validation = self._validate(arguments, tool.input_schema)
        if validation:
            return self._result(request_id, {"content": [{"type": "text", "text": validation}], "isError": True})
        try:
            data = tool.handler(arguments)
            return self._result(request_id, {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, default=str)}]})
        except Exception as exc:
            return self._result(request_id, {"content": [{"type": "text", "text": f"SOFIA tool failed: {exc}"}], "isError": True})

    @staticmethod
    def _validate(arguments: dict[str, Any], schema: dict[str, Any]) -> str | None:
        properties = schema.get("properties", {})
        unknown = sorted(set(arguments) - set(properties))
        if unknown:
            return f"Unexpected argument(s): {', '.join(unknown)}"
        for key in schema.get("required", []):
            if key not in arguments:
                return f"Missing required argument: {key}"
        for key, spec in properties.items():
            if key not in arguments:
                continue
            value = arguments[key]
            if spec.get("type") == "string" and not isinstance(value, str):
                return f"Argument '{key}' must be a string"
            if isinstance(value, str) and len(value) < spec.get("minLength", 0):
                return f"Argument '{key}' is too short"
            if isinstance(value, str) and len(value) > spec.get("maxLength", 1000000):
                return f"Argument '{key}' is too long"
        return None

    @staticmethod
    def _descriptor(tool: McpTool) -> dict[str, Any]:
        return {"name": tool.name, "description": tool.description, "inputSchema": tool.input_schema}

    @staticmethod
    def _zabbix_active_summary(_: dict[str, Any]) -> dict[str, Any]:
        connector = ZabbixConnector()
        summary = connector.get_problem_summary(limit=200)
        return {
            "host_count": connector.count_hosts(),
            "active_problems": int(summary.get("total_problems", 0) or 0),
            "affected_hosts": int(summary.get("affected_hosts", 0) or 0),
            "severity_buckets": summary.get("severity_buckets", {}),
        }

    @staticmethod
    def _platform_status(_: dict[str, Any]) -> dict[str, Any]:
        snapshot = registry.get_snapshot()
        return {"modules": snapshot.get("modules", []), "services": snapshot.get("services", []), "capabilities": snapshot.get("capabilities", {})}

    @staticmethod
    def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": JSON_RPC_VERSION, "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": JSON_RPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}


mcp_server = McpServer()
