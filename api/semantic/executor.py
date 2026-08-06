from __future__ import annotations

from typing import Any

from connectors.zabbix import ZabbixConnector
from presentation.formatters import format_historical_triggers, format_related_problems
from semantic.models import SemanticQuery
from zabbix.aggregation import unique_affected_hosts
from zabbix.query_filters import entity_group, filter_problems


def execute_zabbix_query(query: SemanticQuery, question: str, connector: ZabbixConnector | None = None) -> dict[str, Any] | None:
    if query.source != "zabbix":
        return None
    connector = connector or ZabbixConnector()
    group = entity_group(query)
    if query.intent == "historical_trigger_summary" and query.time_range:
        days = query.time_range.days or 7
        events = connector.list_trigger_events(days=days, limit=5000, group_name=group)
        events = filter_problems(query, events, question)
        active = connector.list_active_problems(limit=2000, group_name=group)
        active = filter_problems(query, active, question)
        label = query.entity_type.replace("_", " ") if query.entity_type != "unknown" else "hosts"
        answer = format_historical_triggers(events, len(events), days, label, active)
        return {"answer":answer,"matches":events,"active":active,"group":group,"days":days,"hosts":unique_affected_hosts(events),"intent":query.intent}
    if query.intent == "active_trigger_summary":
        universe = connector.list_active_problems(limit=2000, group_name=group)
        matches = filter_problems(query, universe, question)
        answer = format_related_problems(matches, len(universe), question)
        return {"answer":answer,"matches":matches,"active":matches,"group":group,"days":None,"hosts":unique_affected_hosts(matches),"intent":query.intent}
    return None
