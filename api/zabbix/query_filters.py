from __future__ import annotations

from typing import Any

from ai.operational_query import related_problems
from semantic.models import SemanticQuery
from semantic.validator import ENTITY_GROUPS


def entity_group(query: SemanticQuery) -> str | None:
    """Return only a canonical, allowlisted Zabbix group."""
    return ENTITY_GROUPS.get(query.entity_type)


def filter_problems(query: SemanticQuery, problems: list[dict[str, Any]], question: str = "") -> list[dict[str, Any]]:
    group = entity_group(query)
    if group:
        problems = [item for item in problems if group in (item.get("groups") or [])]
    if query.metric in {"trigger_count", "active_problems", "availability"} and question:
        narrowed = related_problems(question, problems)
        # Entity/group filtering is authoritative. Lexical narrowing is optional and
        # must not turn a valid scoped query into an empty result.
        return narrowed or problems
    return problems
