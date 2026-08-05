from unittest.mock import Mock

from ai.operational_query import format_related_problems, related_problems, wants_related_alarm_list
from ai.planner import build_plan
from routes import ai


PROBLEMS = [
    {"name": "Unavailable by ICMP ping", "severity_label": "High", "hosts": ["switch-a"], "groups": ["Switches"]},
    {"name": "Unavailable by ICMP ping", "severity_label": "High", "hosts": ["switch-b"], "groups": ["Switches"]},
    {"name": "CPU usage high", "severity_label": "Average", "hosts": ["server-a"], "groups": ["Servers"]},
    {"name": "ICMP Ping: Unavailable by ICMP ping", "severity_label": "High", "hosts": ["server-b"], "groups": ["Servers"]},
]


def test_definition_is_general_chat_without_operational_tools():
    plan = build_plan("O que é host?")
    assert plan["intent"] == "general_chat"
    assert plan["tools"] == []


def test_all_matching_icmp_alarms_are_kept():
    question = "Quais switches não respondem ao ping ICMP?"
    assert wants_related_alarm_list(question)
    matches = related_problems(question, PROBLEMS)
    assert [item["hosts"][0] for item in matches] == ["switch-a", "switch-b"]
    answer = format_related_problems(matches, len(PROBLEMS))
    assert "switch-a" in answer and "switch-b" in answer
    assert "CPU usage" not in answer


def test_ai_route_returns_all_related_alarms_without_external_llm(monkeypatch):
    connector = Mock()
    connector.list_active_problems.return_value = PROBLEMS
    service = Mock()
    store = Mock()
    monkeypatch.setattr(ai, "ZabbixConnector", lambda: connector)
    monkeypatch.setattr(ai, "openai_service", service)
    monkeypatch.setattr(ai, "postgres_store", store)
    response = ai.ask(ai.AIAskRequest(question="Quais switches não respondem ao ping ICMP?"))
    assert response["source"] == "zabbix-local-correlation"
    assert "switch-a" in response["answer"] and "switch-b" in response["answer"]
    assert response["context"]["related_problem_count"] == 2
    service.answer.assert_not_called()


def test_host_count_is_not_misclassified_as_alarm_listing():
    assert not wants_related_alarm_list('Quantos hosts tem no Zabbix?')

def test_generic_active_problem_request_keeps_all_problems():
    matches=related_problems('Quais hosts tem problemas ativos no Zabbix?',PROBLEMS)
    assert matches==PROBLEMS
