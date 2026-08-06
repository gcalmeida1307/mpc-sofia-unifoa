from __future__ import annotations

import re
import unicodedata

from semantic.models import SemanticQuery, SemanticTimeRange


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in value if not unicodedata.combining(char))


_NUMBER_WORDS = {"um":1,"uma":1,"dois":2,"duas":2,"tres":3,"quatro":4,"cinco":5,"seis":6,"sete":7,"oito":8,"nove":9,"dez":10,"quinze":15,"trinta":30}
_ENTITIES = (
    (("switch",), "switch", "Switches", "network"),
    (("servidor", "server"), "server", "Servidores", "infrastructure"),
    (("access point", "access-point", " aps "), "access_point", "Access-Point's", "network"),
    (("firewall",), "firewall", "Firewall", "security"),
    (("nobreak", "ups"), "ups", "Nobreaks", "infrastructure"),
    (("roteador", "router"), "router", "Roteadores", "network"),
)


def _days(q: str) -> int | None:
    numeric = re.search(r"\b(\d{1,3})\s*dias?\b", q)
    if numeric:
        return max(1, min(int(numeric.group(1)), 90))
    written = re.search(r"\b(" + "|".join(_NUMBER_WORDS) + r")\s*dias?\b", q)
    if written:
        return _NUMBER_WORDS[written.group(1)]
    if any(term in q for term in ("ultima semana", "ultimos sete dias", "esta semana")):
        return 7
    return None


def deterministic_interpret(question: str) -> SemanticQuery:
    q = normalize(question)
    entity_type, entity_name, domain = "unknown", None, "general"
    for terms, candidate_type, candidate_name, candidate_domain in _ENTITIES:
        if any(term in f" {q} " for term in terms):
            entity_type, entity_name, domain = candidate_type, candidate_name, candidate_domain
            break

    days = _days(q)
    trigger = any(term in q for term in ("trigger", "alerta", "alarme", "problema", "icmp", "ping", "nao respond", "indispon"))
    active = any(term in q for term in ("ativo", "agora", "neste momento", "atual"))
    count = any(term in q for term in ("quantos", "quantas", "quantidade", "total"))

    if trigger and days:
        intent, source, metric, state, group_by = "historical_trigger_summary", "zabbix", "trigger_count", "historical", "host"
    elif trigger:
        intent, source, metric, state, group_by = "active_trigger_summary", "zabbix", "active_problems", "active" if active else "current", "host"
    elif count and any(term in q for term in ("host", "switch", "servidor", "grupo")):
        intent, source, metric, state, group_by = "host_count", "zabbix", "host_count", "current", "group"
    elif any(term in q for term in ("o que e", "defina", "conceito", "explique")):
        intent, source, metric, state, group_by = "general_chat", "none", "none", "conceptual", "none"
    elif any(term in q for term in ("docker", "container")):
        intent, source, metric, state, group_by, domain = "docker_observe", "docker", "none", "current", "none", "infrastructure"
    elif any(term in q for term in ("runbook", "documentacao", "procedimento", "base offline")):
        intent, source, metric, state, group_by = "knowledge_lookup", "knowledge", "none", "conceptual", "none"
    else:
        intent, source, metric, state, group_by = "general_chat", "none", "none", "unknown", "none"

    return SemanticQuery(
        intent=intent, domain=domain, source=source, entity_type=entity_type,
        entity_name=entity_name, time_range=SemanticTimeRange(days=days) if days else None,
        metric=metric, state=state, group_by=group_by, confidence=0.72,
        interpretation_source="deterministic",
    )
