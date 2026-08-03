import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.assistant_intelligence import build_investigation_plan, classify_question


def test_classify_question_detects_investigation():
    intent = classify_question("quantos deles estão com severity average?")
    assert intent["kind"] == "investigation"
    assert intent["needs_zabbix"] is True


def test_build_investigation_plan_contains_steps():
    plan = build_investigation_plan(
        "por que o servidor caiu",
        modules=["zabbix", "knowledge"],
        capabilities={"zabbix": ["hosts", "problems"], "knowledge": ["search"]},
        knowledge_hint="contexto de incidentes",
    )
    assert "Zabbix" in plan
    assert "1." in plan
    assert "causa provável" in plan.lower()
