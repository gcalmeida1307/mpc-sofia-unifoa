from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from semantic.models import SemanticQuery


ENTITY_GROUPS = {
    "switch": "Switches", "server": "Servidores", "access_point": "Access-Point's",
    "firewall": "Firewall", "router": "Roteadores", "ups": "Nobreaks",
}


def validate_semantic_query(candidate: dict[str, Any], *, provider: str = "unknown") -> SemanticQuery:
    """Reject unknown fields and canonicalize executable values against allowlists."""
    data = dict(candidate)
    data["interpretation_source"] = provider if provider in {"anthropic", "ollama", "deterministic"} else "unknown"
    entity_type = str(data.get("entity_type", "unknown"))
    if entity_type in ENTITY_GROUPS:
        data["entity_name"] = ENTITY_GROUPS[entity_type]
    query = SemanticQuery.model_validate(data)

    if query.source == "zabbix" and query.intent == "historical_trigger_summary" and not query.time_range:
        raise ValidationError.from_exception_data("SemanticQuery", [])
    if query.intent == "historical_trigger_summary" and query.state != "historical":
        raise ValueError("historical intent requires historical state")
    return query
