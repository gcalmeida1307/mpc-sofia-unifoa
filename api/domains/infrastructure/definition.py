from __future__ import annotations

from core.base_module import BaseModule
from core.domain_registry import DomainDefinition, DomainManifest, DomainMcpTool, DomainRoute


class ZabbixModule(BaseModule):
    name = "zabbix"
    version = "1.0.0"
    capabilities = ["login", "hosts", "problems", "triggers"]


class DockerModule(BaseModule):
    name = "docker"
    version = "1.0.0"
    capabilities = ["list_containers", "restart_container", "list_images", "create_network", "list_volumes"]


class N8NModule(BaseModule):
    name = "n8n"
    version = "1.0.0"
    capabilities = ["trigger_webhook", "incident_correlation", "auto_remediation"]


class SSHModule(BaseModule):
    name = "ssh"
    version = "0.1.0"
    capabilities = ["run_command", "collect_diagnostics"]


def _routers():
    from routes.context import router as context_router
    from routes.infra import router as infra_router
    from routes.zabbix import router as zabbix_router
    return [context_router, infra_router, zabbix_router]


def _scheduled_jobs():
    from context.infrastructure import snapshot_service
    return [snapshot_service.refresh]


def _autonomy_jobs():
    from ai.autonomous_investigator import autonomous_investigator
    return [autonomous_investigator.run_cycle]


def _register_event_handlers(event_bus):
    from .events import register
    register(event_bus)


def _summary(_arguments):
    from services.infrastructure import get_infrastructure_summary
    return get_infrastructure_summary()


def _active_summary(_arguments):
    from connectors.zabbix import ZabbixConnector
    connector = ZabbixConnector()
    summary = connector.get_problem_summary(limit=200)
    return {
        "host_count": connector.count_hosts(),
        "active_problems": int(summary.get("total_problems", 0) or 0),
        "affected_hosts": int(summary.get("affected_hosts", 0) or 0),
        "severity_buckets": summary.get("severity_buckets", {}),
    }


def _mcp_tools():
    return [
        DomainMcpTool(
            "sofia.infrastructure.summary",
            "Return a local infrastructure summary collected by the installed domain.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            _summary,
            "infrastructure.summary.read",
        ),
        DomainMcpTool(
            "sofia.zabbix.active_summary",
            "Return current Zabbix host and active problem impact summary.",
            {"type": "object", "properties": {}, "additionalProperties": False},
            _active_summary,
            "infrastructure.monitoring.read",
        ),
    ]


def _migrate_legacy_snapshots():
    from services.postgres_store import postgres_store
    with postgres_store._connect() as conn:
        conn.execute("""DO $$ BEGIN
            IF to_regclass('public.infra_snapshots') IS NOT NULL THEN
                INSERT INTO domain_snapshots(domain_id,generated_at,summary,payload,created_at)
                SELECT 'infrastructure',generated_at,summary,payload,created_at FROM infra_snapshots
                ON CONFLICT(domain_id,generated_at) DO NOTHING;
            END IF;
        END $$""")
        conn.commit()


def _migrations():
    return [_migrate_legacy_snapshots]


def _health_checks():
    def database_snapshot():
        from services.postgres_store import postgres_store
        rows = postgres_store.get_recent_snapshots("infrastructure", 1)
        return {"name": "infrastructure.snapshot", "status": "ok" if rows else "collecting"}
    return [database_snapshot]


domain = DomainDefinition(
    manifest=DomainManifest(
        domain_id="infrastructure",
        version="1.0.0",
        display_name="Infraestrutura",
        description="Monitoramento, investigação e automação da infraestrutura de TI.",
    ),
    permissions=(
        "infrastructure.monitoring.read",
        "infrastructure.summary.read",
        "infrastructure.action.execute",
    ),
    modules=(ZabbixModule, DockerModule, N8NModule, SSHModule),
    routes=(
        DomainRoute("/context", "infrastructure.summary.read"),
        DomainRoute("/zabbix", "infrastructure.monitoring.read"),
        DomainRoute("/infra", "infrastructure.summary.read"),
    ),
    capability_tools={
        "host_count": ["zabbix.count_hosts"],
        "host_analysis": ["zabbix.count_hosts", "zabbix.list_problems"],
        "mcp_zabbix_summary": ["mcp.sofia.zabbix.active_summary"],
        "incident_analysis": ["zabbix.investigate"],
        "network_investigation": ["zabbix.investigate", "learning.insights", "knowledge.search"],
        "security_investigation": ["zabbix.investigate", "learning.insights", "knowledge.search"],
        "capacity_investigation": ["zabbix.investigate", "learning.insights"],
        "docker_observe": ["docker.list_containers"],
        "docker_restart": ["docker.list_containers", "docker.restart_container"],
    },
    role_grants={
        "analyst": {"infrastructure.monitoring.read", "infrastructure.summary.read"},
        "operator": {"infrastructure.monitoring.read", "infrastructure.summary.read", "infrastructure.action.execute"},
    },
    mcp_tools=_mcp_tools,
    routers=_routers,
    scheduled_jobs=_scheduled_jobs,
    autonomy_jobs=_autonomy_jobs,
    register_event_handlers=_register_event_handlers,
    migrations=_migrations,
    navigation=(
        {"label": "Operações", "href": "/ui/analista.html", "capability": "infrastructure.summary.read"},
        {"label": "Analytics", "href": "/ui/analytics.html", "capability": "dashboard.read"},
    ),
    widgets=(
        {"id": "infrastructure.health", "view": "executive", "title": "Saúde do ambiente"},
        {"id": "infrastructure.risks", "view": "executive", "title": "Maiores riscos"},
    ),
    knowledge_collections=(
        {"id": "infrastructure.runbooks", "domain": "infrastructure", "types": ["runbook", "documentation", "incident"]},
    ),
    health_checks=_health_checks,
)
