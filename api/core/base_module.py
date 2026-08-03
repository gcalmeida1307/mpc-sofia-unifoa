from __future__ import annotations

from typing import Any


class BaseModule:
    name: str = ""
    version: str = "1.0.0"
    capabilities: list[str] | None = None

    def __init__(self):
        self.capabilities = list(self.capabilities or [])

    @classmethod
    def module_name(cls) -> str:
        return cls.name or cls.__name__.lower()

    async def startup(self, context: dict[str, Any] | None = None) -> None:
        # Optional lifecycle hook implemented by concrete modules.
        return None

    async def shutdown(self, context: dict[str, Any] | None = None) -> None:
        # Optional lifecycle hook implemented by concrete modules.
        return None

    def register_tools(self) -> dict[str, Any]:
        # Optional tool descriptors for planner/execution layers.
        return {}

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "module": self.module_name(), "version": self.version}

    def capabilities_snapshot(self) -> list[str]:
        return sorted(set(self.capabilities or []))
