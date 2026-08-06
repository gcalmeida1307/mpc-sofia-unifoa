from services import dashboard


def test_dashboard_summary_combines_resources_services_and_training(monkeypatch):
    monkeypatch.setattr(dashboard, "get_server_resources", lambda: {"cpu":{"load_percent_estimate":12},"memory":{},"disk":{}})
    monkeypatch.setattr(dashboard, "_database_details", lambda: {"size_mb":42,"connection_percent":3})
    monkeypatch.setattr(dashboard, "_training_activity", lambda: {"cycles":7,"recent_prompts":[]})
    monkeypatch.setattr(dashboard, "_provider_status", lambda: [{"name":"Claude","status":"operational"}])
    monkeypatch.setattr(dashboard, "_hourly_device_timeline", lambda: [{"hour":"2026-08-06T08:00:00+00:00","devices":234,"problems":12,"readings":30,"change":0}])
    monkeypatch.setattr(dashboard, "_tcp_status", lambda host,port: "online")
    monkeypatch.setattr(dashboard, "_http_status", lambda url: "online")
    result=dashboard.dashboard_summary()
    assert result["resources"]["database"]["size_mb"]==42
    assert result["training"]["cycles"]==7
    assert result["device_timeline"][0]["devices"]==234
    assert all(item["status"]=="online" for item in result["services"])


def test_provider_error_classification_is_safe():
    from ai.client import OpenAIResponsesClient
    assert OpenAIResponsesClient._classify_provider_error(401)=="invalid_or_expired_key"
    assert OpenAIResponsesClient._classify_provider_error(429)=="credit_or_rate_limit"
    assert OpenAIResponsesClient._classify_provider_error(503)=="provider_unavailable"
