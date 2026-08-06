from unittest.mock import Mock

from ai.operational_query import format_historical_triggers, format_related_problems, historical_trigger_group, historical_trigger_window, related_problems, unique_affected_hosts, wants_related_alarm_list
from ai.planner import build_plan
from routes import ai
from semantic.fallback import deterministic_interpret


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
    monkeypatch.setattr("semantic.executor.ZabbixConnector", lambda: connector)
    monkeypatch.setattr(ai.semantic_gateway, "interpret", deterministic_interpret)
    monkeypatch.setattr(ai, "openai_service", service)
    monkeypatch.setattr(ai, "postgres_store", store)
    response = ai.ask(ai.AIAskRequest(question="Quais switches não respondem ao ping ICMP?"))
    assert response["source"] == "semantic-zabbix"
    assert "switch-a" in response["answer"] and "switch-b" in response["answer"]
    assert response["context"]["related_problem_count"] == 2
    service.answer.assert_not_called()


def test_host_count_is_not_misclassified_as_alarm_listing():
    assert not wants_related_alarm_list('Quantos hosts tem no Zabbix?')

def test_generic_active_problem_request_keeps_all_problems():
    matches=related_problems('Quais hosts tem problemas ativos no Zabbix?',PROBLEMS)
    assert matches==PROBLEMS


def test_icmp_count_question_does_not_treat_connector_words_as_filters():
    matches=related_problems('Quantos hosts estão com problema de ICMP?',PROBLEMS)
    assert [item['hosts'][0] for item in matches] == ['switch-a','switch-b','server-b']


def test_icmp_count_accepts_dispositivos_as_generic_host_noun():
    matches=related_problems('Quantos dispositivos estão com problema de ICMP?',PROBLEMS)
    assert [item['hosts'][0] for item in matches] == ['switch-a','switch-b','server-b']


def test_same_host_in_multiple_groups_is_counted_once_by_hostid():
    problems=[
        {'name':'ICMP unavailable','hosts':['switch-a'],'groups':['Global','Switches'],'host_refs':[{'hostid':'42','name':'switch-a','groups':['Global','Switches']}]},
        {'name':'Interface down','hosts':['switch-a'],'groups':['PRD06','Switches'],'host_refs':[{'hostid':'42','name':'switch-a','groups':['PRD06','Switches']}]},
    ]
    hosts=unique_affected_hosts(problems)
    assert len(hosts)==1
    assert hosts[0]['hostid']=='42'
    assert hosts[0]['groups']==['Global','PRD06','Switches']


def test_host_icmp_question_excludes_zabbix_pinger_capacity_alarm():
    problems=[
        {'name':'ICMP Ping: Unavailable by ICMP ping','hosts':['server-a']},
        {'name':'Zabbix server: Utilization of icmp pinger processes over 75%','hosts':['zabbix-server']},
    ]
    matches=related_problems('Quantos hosts estão com problema de ICMP?',problems)
    assert [item['hosts'][0] for item in matches]==['server-a']


def test_historical_trigger_window_and_strict_switch_filter():
    question = 'Quantos switches apresentaram triggers nos últimos 7 dias?'
    events = [
        {'name':'Interface link down','hosts':['switch-a'],'groups':['Global','Switches']},
        {'name':'CPU queue high','hosts':['server-a'],'groups':['Global','Servers']},
        {'name':'Airtime high','hosts':['ap-a'],'groups':['Access-Points']},
    ]
    assert historical_trigger_window(question) == 7
    matches = related_problems(question, events, limit=5000)
    assert [item['hosts'][0] for item in matches] == ['switch-a']
    answer = format_historical_triggers(matches, 3, 7, 'switches')
    assert '1 host(s) único(s) no escopo “switches”' in answer
    assert 'server-a' not in answer and 'ap-a' not in answer


def test_historical_group_scope_supports_varied_wording_and_entities():
    assert historical_trigger_window('Quantos switches tiveram triggers nos últimos 3 dias?') == 3
    assert historical_trigger_group('Quantos switches tiveram triggers nos últimos 3 dias?') == ('Switches', 'switches')
    assert historical_trigger_group('Quais servidores tiveram triggers nos últimos 2 dias?') == ('Servidores', 'servidores')
    assert historical_trigger_group('Triggers do grupo PRD06-INFORMATICA nos últimos 5 dias?') == ('PRD06-INFORMATICA', 'hosts do grupo PRD06-INFORMATICA')
