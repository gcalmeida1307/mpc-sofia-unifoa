from __future__ import annotations

from typing import Any


class ModuleRegistry:
    def __init__(self):
        self._modules: dict[str, type] = {}
        self._instances: dict[str, Any] = {}
        self._capabilities: dict[str, set[str]] = {}
        self._capability_tools: dict[str, list[str]] = {}
        self._services: dict[str, Any] = {}

    def register(self, module_obj: type | Any) -> None:
        if isinstance(module_obj, type):
            module_cls = module_obj
            name = getattr(module_cls, "name", None) or module_cls.__name__.lower()
            self._modules[name] = module_cls
            module_capabilities = getattr(module_cls, "capabilities", None) or []
        else:
            instance = module_obj
            name = getattr(instance, "name", None) or instance.__class__.__name__.lower()
            self._modules[name] = instance.__class__
            self._instances[name] = instance
            module_capabilities = getattr(instance, "capabilities", None) or []

        self._capabilities.setdefault(name, set())
        for capability in module_capabilities:
            self._capabilities[name].add(str(capability))

    def activate(self, module_name: str, instance: Any) -> None:
        self._instances[module_name] = instance
        self._capabilities.setdefault(module_name, set())

    def register_capability(self, module_name: str, capability: str) -> None:
        self._capabilities.setdefault(module_name, set()).add(capability)

    def list_modules(self) -> list[str]:
        return sorted(self._modules.keys())

    def get_capabilities(self, module_name: str) -> list[str]:
        return sorted(self._capabilities.get(module_name, set()))

    def get_module(self, module_name: str) -> Any | None:
        return self._instances.get(module_name)

    def get_module_class(self, module_name: str) -> type | None:
        return self._modules.get(module_name)

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    def register_capability_tools(self, capability: str, tools: list[str]) -> None:
        self._capability_tools[capability] = sorted(set(tools))

    def resolve_tools_by_capabilities(self, capabilities: list[str]) -> list[str]:
        tools: list[str] = []
        for capability in capabilities:
            tools.extend(self._capability_tools.get(capability, []))
        return sorted(set(tools))

    def get_capability_catalog(self) -> dict[str, list[str]]:
        return {name: list(tools) for name, tools in self._capability_tools.items()}

    def get(self, name: str) -> Any:
        if name in self._services:
            return self._services[name]
        if name in self._instances:
            return self._instances[name]
        raise KeyError(f"Dependency '{name}' is not registered in the Core registry")

    def has(self, name: str) -> bool:
        return name in self._services or name in self._instances

    def get_snapshot(self) -> dict[str, Any]:
        modules = self.list_modules()
        return {
            "modules": modules,
            "capabilities": {
                module: self.get_capabilities(module)
                for module in modules
            },
            "capability_catalog": self.get_capability_catalog(),
            "services": sorted(self._services.keys()),
        }

    def clear(self) -> None:
        self._modules.clear()
        self._instances.clear()
        self._capabilities.clear()
        self._capability_tools.clear()
        self._services.clear()


registry = ModuleRegistry()
