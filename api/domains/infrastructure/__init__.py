from .definition import domain

__all__ = ["domain"]
from core.domain_intelligence import domain_provider_registry
from .intelligence import infrastructure_intelligence_provider

domain_provider_registry.register(infrastructure_intelligence_provider)
