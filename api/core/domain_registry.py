from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Callable


@dataclass(frozen=True)
class DomainManifest:
    domain_id: str
    version: str
    display_name: str
    description: str
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class DomainMcpTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], Any]
    required_capability: str


@dataclass(frozen=True)
class DomainRoute:
    prefix: str
    capability: str
    methods: frozenset[str] = frozenset()

    def matches(self, path: str, method: str) -> bool:
        return path.startswith(self.prefix) and (not self.methods or method in self.methods)


@dataclass(frozen=True)
class DomainDefinition:
    manifest: DomainManifest
    permissions: tuple[str, ...] = ()
    modules: tuple[type, ...] = ()
    routes: tuple[DomainRoute, ...] = ()
    capability_tools: dict[str, list[str]] = field(default_factory=dict)
    role_grants: dict[str, set[str]] = field(default_factory=dict)
    mcp_tools: Callable[[], list[DomainMcpTool]] = lambda: []
    routers: Callable[[], list[Any]] = lambda: []
    scheduled_jobs: Callable[[], list[Callable[[], Any]]] = lambda: []
    autonomy_jobs: Callable[[], list[Callable[[], Any]]] = lambda: []
    register_event_handlers: Callable[[Any], None] = lambda _bus: None
    migrations: Callable[[], list[Callable[[], Any]]] = lambda: []
    navigation: tuple[dict[str, Any], ...] = ()
    widgets: tuple[dict[str, Any], ...] = ()
    knowledge_collections: tuple[dict[str, Any], ...] = ()
    health_checks: Callable[[], list[Callable[[], dict[str, Any]]]] = lambda: []

    @property
    def domain_id(self) -> str:
        return self.manifest.domain_id


class DomainRegistry:
    def __init__(self) -> None:
        self._domains: dict[str, DomainDefinition] = {}

    def clear(self) -> None:
        self._domains.clear()

    def register(self, definition: DomainDefinition) -> None:
        if not definition.domain_id or definition.domain_id in self._domains:
            raise ValueError(f"Domínio inválido ou duplicado: {definition.domain_id}")
        declared = set(definition.permissions)
        used = {route.capability for route in definition.routes}
        used.update(capability for grants in definition.role_grants.values() for capability in grants)
        used.update(tool.required_capability for tool in definition.mcp_tools())
        undeclared = used - declared
        if undeclared:
            raise ValueError(
                f"Permissões não declaradas por {definition.domain_id}: {', '.join(sorted(undeclared))}"
            )
        self._domains[definition.domain_id] = definition

    def load(self, references: tuple[str, ...]) -> None:
        self.clear()
        for reference in references:
            module_name, attribute = reference.split(":", 1)
            self.register(getattr(import_module(module_name), attribute))
        installed = set(self._domains)
        for definition in self._domains.values():
            missing = set(definition.manifest.dependencies) - installed
            if missing:
                raise ValueError(f"Dependências ausentes para {definition.domain_id}: {', '.join(sorted(missing))}")

    def definitions(self) -> list[DomainDefinition]:
        return list(self._domains.values())

    def ids(self) -> list[str]:
        return sorted(self._domains)

    def catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "id": definition.domain_id,
                "version": definition.manifest.version,
                "display_name": definition.manifest.display_name,
                "description": definition.manifest.description,
                "dependencies": list(definition.manifest.dependencies),
                "permissions": list(definition.permissions),
                "role_grants": {
                    role: sorted(grants) for role, grants in sorted(definition.role_grants.items())
                },
                "navigation": list(definition.navigation),
                "widgets": list(definition.widgets),
                "knowledge_collections": list(definition.knowledge_collections),
            }
            for definition in self._domains.values()
        ]

    def required_capability(self, path: str, method: str) -> str | None:
        for definition in self._domains.values():
            for route in definition.routes:
                if route.matches(path, method):
                    return route.capability
        return None


domain_registry = DomainRegistry()
