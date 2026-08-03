from __future__ import annotations

from typing import Any

from core.base_module import BaseModule


class KnowledgeModule(BaseModule):
    name = "knowledge"
    version = "1.0.0"
    capabilities = ["ingest", "search", "reindex"]


class WorkflowModule(BaseModule):
    name = "workflow"
    version = "1.0.0"
    capabilities = ["run", "orchestrate"]


class MarketplaceModule(BaseModule):
    name = "marketplace"
    version = "1.0.0"
    capabilities = ["install", "catalog"]


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

    async def startup(self, context: dict[str, Any] | None = None) -> None:
        # Placeholder module registered in kernel for future remote ops integration.
        return None
