from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Callable


@dataclass(frozen=True)
class DomainRoute:
    prefix: str
    capability: str
    methods: frozenset[str] = frozenset()

    def matches(self, path: str, method: str) -> bool:
        return path.startswith(self.prefix) and (not self.methods or method in self.methods)


@dataclass(frozen=True)
class DomainDefinition:
    domain_id: str
    modules: tuple[type, ...] = ()
    routes: tuple[DomainRoute, ...] = ()
    capability_tools: dict[str, list[str]] = field(default_factory=dict)
    routers: Callable[[], list[Any]] = lambda: []
    scheduled_jobs: Callable[[], list[Callable[[], Any]]] = lambda: []
    register_event_handlers: Callable[[Any], None] = lambda _bus: None


class DomainRegistry:
    def __init__(self) -> None:
        self._domains: dict[str, DomainDefinition] = {}

    def clear(self) -> None:
        self._domains.clear()

    def register(self, definition: DomainDefinition) -> None:
        if not definition.domain_id or definition.domain_id in self._domains:
            raise ValueError(f"Domínio inválido ou duplicado: {definition.domain_id}")
        self._domains[definition.domain_id] = definition

    def load(self, references: tuple[str, ...]) -> None:
        self.clear()
        for reference in references:
            module_name, attribute = reference.split(":", 1)
            self.register(getattr(import_module(module_name), attribute))

    def definitions(self) -> list[DomainDefinition]:
        return list(self._domains.values())

    def ids(self) -> list[str]:
        return sorted(self._domains)

    def required_capability(self, path: str, method: str) -> str | None:
        for definition in self._domains.values():
            for route in definition.routes:
                if route.matches(path, method):
                    return route.capability
        return None


domain_registry = DomainRegistry()
