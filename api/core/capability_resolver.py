from __future__ import annotations

from core.registry import registry


class CapabilityResolver:
    def resolve(self, intent: str, requested_capabilities: list[str]) -> list[str]:
        capabilities = list(requested_capabilities)

        if intent != "general_chat":
            for base in ["registry_snapshot", "learning_insights"]:
                if base not in capabilities:
                    capabilities.append(base)

        return registry.resolve_tools_by_capabilities(capabilities)


capability_resolver = CapabilityResolver()
