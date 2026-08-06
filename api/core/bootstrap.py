from core.modules import (
    DockerModule,
    KnowledgeModule,
    MarketplaceModule,
    N8NModule,
    SSHModule,
    WorkflowModule,
    ZabbixModule,
)
from core.registry import registry


BUILTIN_MODULES = [
    KnowledgeModule,
    WorkflowModule,
    MarketplaceModule,
    ZabbixModule,
    DockerModule,
    N8NModule,
    SSHModule,
]


def bootstrap_registry():
    registry.clear()
    for module_cls in BUILTIN_MODULES:
        registry.register(module_cls)
        for capability in getattr(module_cls, "capabilities", []) or []:
            registry.register_capability(module_cls.module_name(), capability)

    capability_tools = {
        "host_count": ["zabbix.count_hosts"],
        "host_analysis": ["zabbix.count_hosts", "zabbix.list_problems"],
        "mcp_zabbix_summary": ["mcp.sofia.zabbix.active_summary"],
        "incident_analysis": ["zabbix.investigate"],
        "network_investigation": ["zabbix.investigate", "learning.insights", "knowledge.search"],
        "security_investigation": ["zabbix.investigate", "learning.insights", "knowledge.search"],
        "capacity_investigation": ["zabbix.investigate", "learning.insights"],
        "docker_observe": ["docker.list_containers"],
        "docker_restart": ["docker.list_containers", "docker.restart_container"],
        "marketplace_browse": ["marketplace.catalog"],
        "knowledge_lookup": ["knowledge.search"],
        "workflow_lookup": ["workflow.templates"],
        "registry_snapshot": ["registry.snapshot"],
        "learning_insights": ["learning.insights"],
    }
    for capability, tools in capability_tools.items():
        registry.register_capability_tools(capability, tools)

    return registry.get_snapshot()
