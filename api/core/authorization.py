from __future__ import annotations

from dataclasses import dataclass


ROLE_CAPABILITIES = {
    "viewer": {"dashboard.read", "profile.manage"},
    "user": {"dashboard.read", "assistant.ask", "profile.manage"},
    "analyst": {"dashboard.read", "assistant.ask", "zabbix.read", "workflow.execute", "profile.manage"},
    "operator": {"dashboard.read", "assistant.ask", "zabbix.read", "workflow.execute", "workflow.publish", "profile.manage"},
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
    RoutePolicy("/zabbix", "zabbix.read"),
    RoutePolicy("/infra", "infrastructure.read"),
    RoutePolicy("/engine", "intelligence.manage"),
    RoutePolicy("/learning", "intelligence.manage"),
    RoutePolicy("/marketplace", "platform.manage"),
    RoutePolicy("/core", "platform.manage"),
    RoutePolicy("/docs", "platform.manage"),
)


def capabilities_for(role: str) -> set[str]:
    return set(ROLE_CAPABILITIES.get(role, ROLE_CAPABILITIES["viewer"]))


def is_allowed(role: str, capability: str) -> bool:
    granted = capabilities_for(role)
    return "*" in granted or capability in granted


def required_capability(path: str, method: str) -> str | None:
    for policy in ROUTE_POLICIES:
        if policy.matches(path, method):
            return policy.capability
    return None
