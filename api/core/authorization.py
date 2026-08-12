from __future__ import annotations

from dataclasses import dataclass


ROLE_CAPABILITIES = {
    "viewer": {"dashboard.read", "knowledge.search", "profile.manage"},
    "user": {"dashboard.read", "assistant.ask", "knowledge.search", "profile.manage", "investigation.manage"},
    "analyst": {"dashboard.read", "assistant.ask", "knowledge.search", "workflow.execute", "profile.manage", "investigation.manage"},
    "operator": {"dashboard.read", "assistant.ask", "knowledge.search", "workflow.execute", "workflow.publish", "profile.manage", "investigation.manage"},
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
    RoutePolicy("/timeline", "dashboard.read"),
    RoutePolicy("/investigations", "investigation.manage"),
    RoutePolicy("/context", "dashboard.read"),
    RoutePolicy("/workflows", "workflow.execute", frozenset({"GET", "POST"})),
    RoutePolicy("/knowledge", "knowledge.manage"),
    RoutePolicy("/domains", "platform.manage", frozenset({"POST", "DELETE", "PATCH", "PUT"})),
    RoutePolicy("/domains", "knowledge.search", frozenset({"GET"})),
    RoutePolicy("/engine", "intelligence.manage"),
    RoutePolicy("/learning", "dashboard.read", frozenset({"GET"})),
    RoutePolicy("/learning", "intelligence.manage", frozenset({"POST", "PUT", "PATCH", "DELETE"})),
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


def domain_from_path(path: str) -> str | None:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 2 and parts[0] == "domains" and parts[1] not in {"experience", "proposals"}:
        return parts[1]
    if len(parts) >= 2 and parts[0] == "timeline":
        return parts[1]
    if len(parts) >= 3 and parts[:2] == ["learning", "status"]:
        return parts[2]
    return None


def authorize(user: dict, path: str, method: str, domain_id: str | None = None) -> tuple[bool, str | None]:
    capability = required_capability(path, method)
    if capability and not is_allowed(str(user.get("role", "viewer")), capability):
        return False, capability
    domain_id = domain_id or domain_from_path(path)
    if domain_id and user.get("role") != "admin":
        from services.auth import auth_service
        memberships = {item["domain_id"] for item in auth_service.domain_access(int(user["id"]))}
        if domain_id not in memberships:
            return False, f"{domain_id}.membership"
    return True, capability
