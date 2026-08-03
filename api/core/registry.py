from __future__ import annotations

from typing import Any


class ModuleRegistry:
    def __init__(self):
        self._modules: dict[str, type] = {}
        self._capabilities: dict[str, set[str]] = {}

    def register(self, module_cls: type) -> None:
        name = getattr(module_cls, "name", None) or module_cls.__name__.lower()
        self._modules[name] = module_cls
        self._capabilities.setdefault(name, set())

    def register_capability(self, module_name: str, capability: str) -> None:
        self._capabilities.setdefault(module_name, set()).add(capability)

    def list_modules(self) -> list[str]:
        return sorted(self._modules.keys())

    def get_capabilities(self, module_name: str) -> list[str]:
        return sorted(self._capabilities.get(module_name, set()))

    def get_snapshot(self) -> dict[str, Any]:
        return {
            "modules": self.list_modules(),
            "capabilities": {
                module: self.get_capabilities(module)
                for module in self.list_modules()
            },
        }

    def clear(self) -> None:
        self._modules.clear()
        self._capabilities.clear()


registry = ModuleRegistry()
