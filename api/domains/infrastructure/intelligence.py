from __future__ import annotations

from datetime import datetime
from typing import Any

from core.domain_intelligence import DomainEntity, DomainEvent
from services.zabbix_investigator import format_investigation


class InfrastructureIntelligenceProvider:
    domain_id = "infrastructure"

    def events_from_snapshot(self, snapshot_id: int, occurred_at: datetime, payload: dict[str, Any]) -> list[DomainEvent]:
        problems = ((payload or {}).get("zabbix") or {}).get("problems", []) or []
        events = []
        for item in problems:
            event_id = item.get("eventid")
            if not event_id:
                continue
            hosts = item.get("hosts") or []
            groups = item.get("groups") or []
            entities = tuple(
                [DomainEntity("host", str(value), str(value), topology=tuple(map(str, groups))) for value in hosts]
                + [DomainEntity("group", str(value), str(value)) for value in groups]
            )
            events.append(DomainEvent(
                external_key=f"snapshot:{snapshot_id}:problem:{event_id}", event_type="problem.active",
                title=str(item.get("name") or "Ocorrência observada"),
                summary=f"Ocorrência reportada em {', '.join(map(str, hosts[:3])) or 'entidade não identificada'}.",
                occurred_at=occurred_at, entities=entities,
                evidence={"snapshot_id": snapshot_id, "event_id": event_id, "severity": item.get("severity_label") or item.get("severity")},
                source="infrastructure.zabbix",
            ))
        return events

    def ai_context(self, outputs: dict[str, Any]) -> dict[str, Any]:
        investigation = outputs.get("zabbix.investigate", {})
        evidence = investigation.get("evidence", []) if isinstance(investigation, dict) else []
        return {"domain_id": self.domain_id, "evidence": evidence, "scope": investigation.get("scope", {}) if isinstance(investigation, dict) else {}, "missing_data": investigation.get("missing_data", []) if isinstance(investigation, dict) else []}

    def format_answer(self, context: dict[str, Any]) -> str | None:
        return format_investigation(context) if context.get("evidence") else None

    def execute_semantic(self, semantic: Any, question: str) -> dict[str, Any] | None:
        from semantic.executor import execute_zabbix_query
        return execute_zabbix_query(semantic, question)


infrastructure_intelligence_provider = InfrastructureIntelligenceProvider()
