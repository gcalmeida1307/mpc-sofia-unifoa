from __future__ import annotations

from core.registry import registry


class RegistryProvider:
    def execute(self, tool_name: str, question: str) -> dict:
        if tool_name != "registry.snapshot":
            return {"error": f"unsupported registry tool: {tool_name}"}
        return registry.get_snapshot()


registry_provider = RegistryProvider()