from pathlib import Path

from core.authorization import required_capability
from core.domain_registry import DomainRegistry
from domains.infrastructure.definition import domain as infrastructure_domain
from services.mcp_server import mcp_server


CORE_ROOT = Path(__file__).resolve().parents[1] / "core"


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
