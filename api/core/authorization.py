from __future__ import annotations

from dataclasses import dataclass


ROLE_CAPABILITIES = {
    "viewer": {"dashboard.read", "knowledge.search", "profile.manage"},
    "user": {"dashboard.read", "assistant.ask", "knowledge.search", "profile.manage"},
    "analyst": {"dashboard.read", "assistant.ask", "knowledge.search", "workflow.execute", "profile.manage"},
    "operator": {"dashboard.read", "assistant.ask", "knowledge.search", "workflow.execute", "workflow.publish", "profile.manage"},
    "admin": {"*"},
}


@dataclass(frozen=True)
class RoutePolicy:
    prefix: str
    capability: str
    methods: frozenset[str] = frozenset()

    def matches(self, path: str, method: str) -> bool:
        return path.startswith(self.prefix) and (not self.methods or method in self.methods)


ROUTE_POLICIES = (
    RoutePolicy("/assistant", "assistant.ask"),
    RoutePolicy("/ai", "assistant.ask"),
    RoutePolicy("/dashboard", "dashboard.read"),
    RoutePolicy("/context", "dashboard.read"),
    RoutePolicy("/workflows", "workflow.execute", frozenset({"GET", "POST"})),
    RoutePolicy("/knowledge", "knowledge.manage"),
    RoutePolicy("/domains", "platform.manage", frozenset({"POST", "DELETE", "PATCH", "PUT"})),
    RoutePolicy("/domains", "knowledge.search", frozenset({"GET"})),
    RoutePolicy("/engine", "intelligence.manage"),
    RoutePolicy("/learning", "intelligence.manage"),
    RoutePolicy("/marketplace", "platform.manage"),
    RoutePolicy("/core", "platform.manage"),
    RoutePolicy("/docs", "platform.manage"),
)


def capabilities_for(role: str) -> set[str]:
    from core.domain_registry import domain_registry
    granted = set(ROLE_CAPABILITIES.get(role, ROLE_CAPABILITIES["viewer"]))
    for definition in domain_registry.definitions():
        granted.update(definition.role_grants.get(role, set()))
    return granted


def is_allowed(role: str, capability: str) -> bool:
    granted = capabilities_for(role)
    return "*" in granted or capability in granted


def required_capability(path: str, method: str) -> str | None:
    from core.domain_registry import domain_registry
    domain_capability = domain_registry.required_capability(path, method)
    if domain_capability:
        return domain_capability
    for policy in ROUTE_POLICIES:
        if policy.matches(path, method):
            return policy.capability
    return None
