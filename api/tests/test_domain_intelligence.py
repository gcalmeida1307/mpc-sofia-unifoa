from datetime import datetime, timezone
from pathlib import Path

from core.authorization import domain_from_path
from core.domain_intelligence import DomainEntity, DomainEvent, DomainProviderRegistry


class Provider:
    domain_id = "medicine"
    def events_from_snapshot(self, snapshot_id, occurred_at, payload):
        return [DomainEvent("visit-1", "visit.started", "Atendimento", "Observado", occurred_at,
                            (DomainEntity("patient", "p-1", "Paciente"),))]
    def ai_context(self, outputs): return {"domain_id": self.domain_id, "evidence": outputs.get("events", [])}
    def format_answer(self, context): return "Evidência clínica" if context.get("evidence") else None


def test_non_infrastructure_provider_uses_same_contract():
    registry = DomainProviderRegistry(); registry.register(Provider())
    provider = registry.get("medicine")
    events = provider.events_from_snapshot(1, datetime.now(timezone.utc), {})
    assert events[0].entities[0].type == "patient"
    assert registry.context("medicine", {"events": [1]})["evidence"] == [1]


def test_domain_membership_is_resolved_centrally_from_path():
    assert domain_from_path("/domains/medicine/search") == "medicine"
    assert domain_from_path("/domains/experience/catalog") is None


def test_generic_ai_service_has_no_zabbix_import():
    source = (Path(__file__).parents[1] / "ai" / "service.py").read_text(encoding="utf-8")
    assert "services.zabbix" not in source
    assert "format_investigation" not in source


def test_workspace_does_not_generate_placeholder_percentages():
    source = (Path(__file__).parents[1] / "static" / "domain-workspace.js").read_text(encoding="utf-8")
    assert "35+(index*17)%55" not in source
    assert "não simula métricas" in source
