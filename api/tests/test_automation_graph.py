import pytest

from services.automation_graph import AutomationGraphStore, CONNECTOR_CATALOG


def test_connector_catalog_distinguishes_active_and_unconfigured():
    status = {item["type"]: item["status"] for item in CONNECTOR_CATALOG}
    assert status["zabbix"] == "active"
    assert status["knowledge"] == "active"
    assert status["grafana"] == "active"
    assert status["prometheus"] == "active"
    assert status["loki"] == "active"


def test_graph_validation_accepts_operational_pipeline():
    nodes = [
        {"id": "a", "type": "trigger"},
        {"id": "b", "type": "zabbix"},
        {"id": "c", "type": "correlate"},
        {"id": "d", "type": "report"},
    ]
    edges = [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "c"},
        {"source": "c", "target": "d"},
    ]
    AutomationGraphStore.validate(nodes, edges)


def test_graph_validation_rejects_unknown_connector_and_dangling_edge():
    with pytest.raises(ValueError, match="Tipos de bloco inválidos"):
        AutomationGraphStore.validate([{"id": "a", "type": "invented"}], [])
    with pytest.raises(ValueError, match="inexistente"):
        AutomationGraphStore.validate([{"id": "a", "type": "trigger"}], [{"source": "a", "target": "missing"}])


def test_execution_orders_connected_nodes_and_builds_report():
    nodes = [
        {"id": "report", "type": "report"},
        {"id": "trigger", "type": "trigger"},
        {"id": "correlate", "type": "correlate"},
    ]
    edges = [
        {"source": "trigger", "target": "correlate"},
        {"source": "correlate", "target": "report"},
    ]
    ordered = AutomationGraphStore._ordered_nodes(nodes, edges)
    assert [node["id"] for node in ordered] == ["trigger", "correlate", "report"]
    outputs = [
        {"connector": "trigger", "summary": "Entrada recebida"},
        {"connector": "correlate", "summary": "Duas evidências correlacionadas"},
    ]
    result = AutomationGraphStore._execute_connector(
        {"id": "report", "type": "report"}, "Por que o switch caiu?", outputs
    )
    assert result["is_report"] is True
    assert "Por que o switch caiu?" in result["summary"]
    assert "Duas evidências correlacionadas" in result["summary"]


def test_zabbix_execution_returns_all_related_switches(monkeypatch):
    problems = [
        {"name": "Unavailable by ICMP ping", "severity_label": "High", "hosts": ["switch-a"], "groups": ["Switches"]},
        {"name": "Unavailable by ICMP ping", "severity_label": "High", "hosts": ["switch-b"], "groups": ["Switches"]},
    ]
    connector = type("Connector", (), {"list_active_problems": lambda self, limit: problems})()
    monkeypatch.setattr("services.automation_graph.ZabbixConnector", lambda: connector)
    monkeypatch.setattr("services.automation_graph.postgres_store.get_recent_snapshots", lambda limit: [])
    monkeypatch.setattr("services.automation_graph.postgres_store.get_recent_insights", lambda limit: [])
    result = AutomationGraphStore._execute_connector(
        {"id": "zabbix", "type": "zabbix"}, "Quais switches não respondem ao ping ICMP?", []
    )
    assert result["data"]["related_problem_count"] == 2
    assert result["data"]["unique_host_count"] == 2
    assert result["data"]["severity_distribution"] == [{"label": "High", "value": 2}]
    assert result["data"]["behavior"]["status"] == "collecting"
    assert "switch-a" in result["summary"] and "switch-b" in result["summary"]


def test_zabbix_analysis_builds_timeline_and_baseline(monkeypatch):
    monkeypatch.setattr("services.automation_graph.postgres_store.get_recent_snapshots", lambda limit: [
        {"generated_at": f"2026-08-05T12:{minute:02d}:00+00:00", "summary": {"problems": minute}}
        for minute in range(10)
    ])
    monkeypatch.setattr("services.automation_graph.postgres_store.get_recent_insights", lambda limit: [{"signature": "a"}])
    analysis = AutomationGraphStore._zabbix_analysis([{
        "eventid": "7", "clock": "1754388000", "name": "Unavailable by ICMP ping",
        "severity_label": "High", "hosts": ["switch-a"], "groups": ["Global", "Switches"],
    }])
    assert analysis["event_timeline"][0]["started_at"]
    assert analysis["group_distribution"][0] == {"label": "Global", "value": 1}
    assert analysis["behavior"]["status"] == "baseline_ready"
    assert len(analysis["behavior"]["problem_series"]) == 10


def test_historical_switch_flow_uses_event_history_and_group_filter(monkeypatch):
    events = [{"eventid":"1","clock":"1754388000","name":"Interface link down","severity_label":"High",
        "hosts":["switch-a"],"groups":["Global","Switches"],"historical":True}]
    class Connector:
        def list_trigger_events(self, days, limit, group_name):
            assert days == 7 and limit == 5000 and group_name == 'Switches'
            return events
    monkeypatch.setattr("services.automation_graph.ZabbixConnector", Connector)
    monkeypatch.setattr("services.automation_graph.postgres_store.get_recent_snapshots", lambda limit: [])
    monkeypatch.setattr("services.automation_graph.postgres_store.get_recent_insights", lambda limit: [])
    result = AutomationGraphStore._execute_connector(
        {"id":"zabbix","type":"zabbix"}, 'Quantos switches apresentaram triggers nos últimos 7 dias?', []
    )
    assert result['data']['query_scope'] == 'historical_triggers'
    assert result['data']['days'] == 7
    assert result['data']['unique_host_count'] == 1
    assert result['data']['event_timeline'][0]['status'] == 'occurred'
    assert result['data']['host_distribution'] == [{'label':'switch-a','value':1}]
