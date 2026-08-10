from pathlib import Path

from core.authorization import required_capability
from core.domain_registry import DomainRegistry
from domains.infrastructure.definition import domain as infrastructure_domain
from services.mcp_server import mcp_server
from fastapi import FastAPI
from core.application import Application
from domains.demo.definition import domain as demo_domain


CORE_ROOT = Path(__file__).resolve().parents[1] / "core"


def _route_paths(app):
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    for route in app.routes:
        router = getattr(route, "original_router", None)
        if router:
            paths.update(item.path for item in router.routes if hasattr(item, "path"))
    return paths


def test_core_does_not_name_or_import_infrastructure_domain():
    forbidden = ("zabbix", "context.infrastructure", "routes.infra", "routes.zabbix", "infra_snapshots")
    violations = []
    for path in CORE_ROOT.glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        if any(value in text for value in forbidden):
            violations.append(path.name)
    assert violations == []


def test_domain_can_be_disabled_without_changing_core():
    registry = DomainRegistry()
    registry.load(())
    assert registry.ids() == []
    registry.register(infrastructure_domain)
    assert registry.ids() == ["infrastructure"]


def test_all_domain_routes_declare_capability():
    assert infrastructure_domain.routes
    for route in infrastructure_domain.routes:
        assert route.prefix.startswith("/")
        assert "." in route.capability


def test_all_mcp_tools_have_permission():
    mcp_server.configure_domains([infrastructure_domain])
    assert mcp_server._tools
    for tool in mcp_server._tools.values():
        assert tool.required_capability
        assert "." in tool.required_capability


def test_installed_domain_routes_are_resolved_dynamically():
    from core.domain_registry import domain_registry
    domain_registry.clear()
    domain_registry.register(infrastructure_domain)
    assert required_capability("/zabbix/investigate", "POST") == "infrastructure.monitoring.read"
    assert required_capability("/infra/summary", "GET") == "infrastructure.summary.read"


def test_platform_starts_route_catalog_without_domains():
    from core.domain_registry import domain_registry
    domain_registry.clear()
    app = FastAPI()
    Application()._register_routes(app)
    paths = _route_paths(app)
    assert "/health" in paths
    assert "/auth/login" in paths
    assert "/knowledge/search" in paths
    assert not any(path.startswith("/zabbix") or path.startswith("/infra") or path.startswith("/context") for path in paths)


def test_infrastructure_domain_adds_routes_tools_and_grants():
    from core.domain_registry import domain_registry
    from core.authorization import capabilities_for
    domain_registry.clear()
    domain_registry.register(infrastructure_domain)
    app = FastAPI()
    Application()._register_routes(app)
    paths = _route_paths(app)
    assert "/zabbix/groups" in paths
    assert "/infra/resumo" in paths
    assert "/context/snapshot" in paths
    mcp_server.configure_domains(domain_registry.definitions())
    names = set(mcp_server._tools)
    assert "sofia.infrastructure.summary" in names
    assert "sofia.zabbix.active_summary" in names
    assert "infrastructure.monitoring.read" in capabilities_for("analyst")
    catalog = domain_registry.catalog()[0]
    assert catalog["permissions"] == [
        "infrastructure.monitoring.read",
        "infrastructure.summary.read",
        "infrastructure.action.execute",
    ]
    assert "infrastructure.monitoring.read" in catalog["role_grants"]["analyst"]


def test_demo_domain_installs_without_core_changes():
    from core.domain_registry import domain_registry
    domain_registry.clear()
    domain_registry.register(demo_domain)
    app = FastAPI()
    Application()._register_routes(app)
    assert "/demo/hello" in _route_paths(app)
    mcp_server.configure_domains(domain_registry.definitions())
    assert "sofia.demo.hello" in mcp_server._tools
    response = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "sofia.demo.hello", "arguments": {}}}, {"demo.read"})
    assert "Olá do domínio" in response["result"]["content"][0]["text"]
    domain_registry.clear()
    domain_registry.register(infrastructure_domain)
    mcp_server.configure_domains(domain_registry.definitions())
