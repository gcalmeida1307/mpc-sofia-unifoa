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
