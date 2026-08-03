from core.base_module import BaseModule
from core.registry import registry


class KnowledgeModule(BaseModule):
    name = "knowledge"
    capabilities = ["ingest", "search", "reindex"]


class WorkflowModule(BaseModule):
    name = "workflow"
    capabilities = ["run", "orchestrate"]


class MarketplaceModule(BaseModule):
    name = "marketplace"
    capabilities = ["install", "catalog"]


class ZabbixModule(BaseModule):
    name = "zabbix"
    capabilities = ["login", "hosts", "problems", "triggers"]


class DockerModule(BaseModule):
    name = "docker"
    capabilities = ["list_containers", "restart_container", "list_images", "create_network", "list_volumes"]


class N8NModule(BaseModule):
    name = "n8n"
    capabilities = ["trigger_webhook", "incident_correlation", "auto_remediation"]


def bootstrap_registry():
    registry.clear()
    registry.register(KnowledgeModule)
    registry.register(WorkflowModule)
    registry.register(MarketplaceModule)
    registry.register(ZabbixModule)
    registry.register(DockerModule)
    registry.register(N8NModule)

    for module_name, capabilities in {
        "knowledge": ["ingest", "search", "reindex"],
        "workflow": ["run", "orchestrate"],
        "marketplace": ["install", "catalog"],
        "zabbix": ["login", "hosts", "problems", "triggers"],
        "docker": ["list_containers", "restart_container", "list_images", "create_network", "list_volumes"],
        "n8n": ["trigger_webhook", "incident_correlation", "auto_remediation"],
    }.items():
        for capability in capabilities:
            registry.register_capability(module_name, capability)

    return registry.get_snapshot()
