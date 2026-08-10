from core.modules import (
    KnowledgeModule,
    MarketplaceModule,
    WorkflowModule,
)
from core.registry import registry
from core.domain_registry import domain_registry
from config.settings import settings


BUILTIN_MODULES = [
    KnowledgeModule,
    WorkflowModule,
    MarketplaceModule,
]


def bootstrap_registry():
    registry.clear()
    domain_registry.load(settings.INSTALLED_DOMAINS)
    domain_modules = [module for definition in domain_registry.definitions() for module in definition.modules]
    for module_cls in [*BUILTIN_MODULES, *domain_modules]:
        registry.register(module_cls)
        for capability in getattr(module_cls, "capabilities", []) or []:
            registry.register_capability(module_cls.module_name(), capability)

    capability_tools = {
        "marketplace_browse": ["marketplace.catalog"],
        "knowledge_lookup": ["knowledge.search"],
        "workflow_lookup": ["workflow.templates"],
        "registry_snapshot": ["registry.snapshot"],
        "learning_insights": ["learning.insights"],
    }
    for definition in domain_registry.definitions():
        capability_tools.update(definition.capability_tools)
    for capability, tools in capability_tools.items():
        registry.register_capability_tools(capability, tools)

    return registry.get_snapshot()
