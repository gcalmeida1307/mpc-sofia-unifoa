from unittest.mock import patch

import pytest

from core.authorization import is_allowed, required_capability
from core.url_security import UnsafeURL, validate_external_url
from workflow.compiler import compile_graph, validate_graph


def test_capability_policy_is_explicit_and_least_privilege():
    assert is_allowed("user", "assistant.ask")
    assert not is_allowed("user", "knowledge.manage")
    assert is_allowed("admin", "knowledge.manage")
    assert required_capability("/knowledge/providers", "POST") == "knowledge.manage"


@pytest.mark.parametrize("address", ["127.0.0.1", "169.254.169.254", "10.0.0.8", "::1"])
def test_ssrf_guard_rejects_non_public_destinations(address):
    with patch("core.url_security.socket.getaddrinfo", return_value=[(None, None, None, None, (address, 80))]):
        with pytest.raises(UnsafeURL):
            validate_external_url("http://docs.example.test/manual")


def test_ssrf_guard_accepts_public_https_and_rejects_url_credentials():
    with patch("core.url_security.socket.getaddrinfo", return_value=[(None, None, None, None, ("93.184.216.34", 443))]):
        assert validate_external_url("https://docs.example.test/manual").startswith("https://")
        with pytest.raises(UnsafeURL):
            validate_external_url("https://user:pass@docs.example.test/manual")


def test_workflow_compiler_orders_dependencies_and_rejects_cycles():
    nodes = [{"id": "a", "type": "trigger"}, {"id": "b", "type": "report"}]
    edges = [{"source": "a", "target": "b"}]
    validate_graph(nodes, edges, {"trigger", "report"})
    assert [item["id"] for item in compile_graph(nodes, edges)] == ["a", "b"]
    with pytest.raises(ValueError, match="ciclo"):
        validate_graph(nodes, [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}], {"trigger", "report"})
