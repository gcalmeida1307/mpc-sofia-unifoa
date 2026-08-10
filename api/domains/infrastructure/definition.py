from __future__ import annotations

from core.base_module import BaseModule
from core.domain_registry import DomainDefinition, DomainRoute


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
    from routes.infra import router as infra_router
    from routes.zabbix import router as zabbix_router
    return [infra_router, zabbix_router]


def _scheduled_jobs():
    from context.infrastructure import snapshot_service
    return [snapshot_service.refresh]


def _register_event_handlers(event_bus):
    from .events import register
    register(event_bus)


domain = DomainDefinition(
    domain_id="infrastructure",
    modules=(ZabbixModule, DockerModule, N8NModule, SSHModule),
    routes=(
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
    routers=_routers,
    scheduled_jobs=_scheduled_jobs,
    register_event_handlers=_register_event_handlers,
)
