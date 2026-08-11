from datetime import datetime, timedelta, timezone

from ai.service import OpenAIService
from services.postgres_store import postgres_store
from services.temporal_intelligence import WINDOWS, temporal_intelligence


def test_temporal_model_preserves_evidence_levels_and_relations():
    temporal_intelligence.ensure_schema();now=datetime.now(timezone.utc);domain="test-temporal"
    with postgres_store._connect() as conn:
        conn.execute("DELETE FROM domain_events WHERE domain_id=%s",(domain,))
        first=temporal_intelligence._save_event(conn,domain_id=domain,key="a",event_type="state.down",title="Componente indisponível",summary="Fonte confirmou indisponibilidade.",at=now-timedelta(seconds=30),entities=[{"type":"asset","id":"x","label":"X"}])
        second=temporal_intelligence._save_event(conn,domain_id=domain,key="b",event_type="state.up",title="Componente disponível",summary="Fonte confirmou recuperação.",at=now,entities=[{"type":"asset","id":"x","label":"X"}]);conn.commit()
    temporal_intelligence.correlate(domain,15);story=temporal_intelligence.story(domain,15)
    assert WINDOWS[10080]==10080
    assert len(story["events"])==2 and story["events"][0]["level"]=="observed"
    assert any(item["from"]==first and item["to"]==second and item["level"]=="correlated" for item in story["relations"])
    assert story["episodes"][0]["affected_entities"]==["X"]
    with postgres_store._connect() as conn:conn.execute("DELETE FROM domain_events WHERE domain_id=%s",(domain,));conn.commit()


def test_ai_response_has_generic_multimodal_contract():
    presentation=OpenAIService._presentation({"tools":{"zabbix.investigate":{"evidence":[{"problem":"Porta down","severity":"Warning","started_at":"2026-08-11T10:00:00+00:00","hosts":["SW-01"]}]}}},.91)
    assert presentation["version"]=="1.0"
    assert presentation["summary_cards"][0]["value"]==1
    assert presentation["chart"]["type"]=="bar"
    assert presentation["timeline"][0]["entity"]=="SW-01"
