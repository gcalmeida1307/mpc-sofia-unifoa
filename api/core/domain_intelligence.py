from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class DomainEntity:
    type: str
    id: str
    label: str
    parent_id: str | None = None
    topology: tuple[str, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DomainEvent:
    external_key: str
    event_type: str
    title: str
    summary: str
    occurred_at: datetime
    entities: tuple[DomainEntity, ...] = ()
    evidence: dict[str, Any] = field(default_factory=dict)
    source: str = "domain.provider"
    confidence: float = 1.0


class DomainIntelligenceProvider(Protocol):
    domain_id: str

    def events_from_snapshot(self, snapshot_id: int, occurred_at: datetime, payload: dict[str, Any]) -> list[DomainEvent]: ...

    def ai_context(self, tool_outputs: dict[str, Any]) -> dict[str, Any]: ...

    def format_answer(self, context: dict[str, Any]) -> str | None: ...


class DomainProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, DomainIntelligenceProvider] = {}

    def register(self, provider: DomainIntelligenceProvider) -> None:
        self._providers[provider.domain_id] = provider

    def get(self, domain_id: str) -> DomainIntelligenceProvider | None:
        return self._providers.get(domain_id)

    def context(self, domain_id: str, outputs: dict[str, Any]) -> dict[str, Any]:
        provider = self.get(domain_id)
        return provider.ai_context(outputs) if provider else {"domain_id": domain_id, "evidence": [], "metrics": {}}


domain_provider_registry = DomainProviderRegistry()
