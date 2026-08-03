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

    return registry.get_snapshot()
