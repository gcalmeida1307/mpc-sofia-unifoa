from __future__ import annotations

import re
import unicodedata
from typing import Any


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in value if not unicodedata.combining(char))


def wants_related_alarm_list(question: str) -> bool:
    q = normalize(question)
    operational = any(term in q for term in ("alarme", "alerta", "problema", "indispon", "down", "nao respond", "ping", "icmp"))
    collection = any(term in q for term in ("todos", "todas", "quais", "quantos", "quantas", "relacionad", "nao respond", "dois ", "duas "))
    return operational and collection


def historical_trigger_window(question: str) -> int | None:
    q = normalize(question)
    if "trigger" not in q or not any(term in q for term in ("ultimo", "ultimos", "dia", "dias", "semana")):
        return None
    match = re.search(r"\b(\d{1,3})\s*dias?\b", q)
    if match:
        return max(1, min(int(match.group(1)), 90))
    return 7 if "semana" in q else None


def historical_trigger_group(question: str) -> tuple[str | None, str]:
    q = normalize(question)
    mappings = (
        (("switch",), "Switches", "switches"),
        (("servidor", "server"), "Servidores", "servidores"),
        (("access point", "access-point", " aps "), "Access-Point's", "access points"),
        (("firewall",), "Firewall", "firewalls"),
        (("nobreak", "ups"), "Nobreaks", "nobreaks"),
        (("roteador", "router"), "Roteadores", "roteadores"),
        (("relogio de ponto",), "Relogios de Ponto", "relógios de ponto"),
    )
    for terms, group, label in mappings:
        if any(term in f" {q} " for term in terms):
            return group, label
    explicit = re.search(
        r"\bgrupo\s+(.+?)(?:\s+(?:teve|tiveram|apresentou|apresentaram|com)\b|\s+n[oa]s?\s+[uú]ltim|\s+durante|[?.]|$)",
        question, re.IGNORECASE,
    )
    if explicit and explicit.group(1).strip():
        group = explicit.group(1).strip()
        return group, f"hosts do grupo {group}"
    return None, "hosts"


def related_problems(question: str, problems: list[dict[str, Any]], limit: int = 500) -> list[dict[str, Any]]:
    q = normalize(question)
    ignored = {
        "qual", "quais", "quantos", "quantas", "tenho", "tem", "estao", "nao", "para", "por", "que",
        "uma", "uns", "das", "dos", "de", "do", "da", "em", "no", "na", "nos", "nas", "aos", "meu", "minha", "sobre",
        "todos", "todas", "alerta", "alertas", "alarme", "alarmes", "problema", "problemas", "respondem",
        "zabbix", "host", "hosts", "ativo", "ativos",
        "com", "sem", "pelo", "pela", "pelos", "pelas",
        "dispositivo", "dispositivos", "equipamento", "equipamentos", "aparelho", "aparelhos",
        "trigger", "triggers", "apresenta", "apresentam", "apresentou", "apresentaram",
        "ultimo", "ultimos", "ultima", "ultimas", "dia", "dias", "semana", "semanas",
    }
    terms = {("switch" if token in {"switches","switchs"} else token.rstrip("s")) for token in re.findall(r"[a-z0-9_.-]{3,}", q) if token not in ignored}
    if not terms:
        return problems[:limit]
    entity_terms={term for term in terms if term in {'switch','roteador','router','firewall','servidor','server','storage','impressora','printer'}}
    minimum_score = 2 if len(terms) >= 2 else 1
    ranked: list[tuple[int, int, dict[str, Any]]] = []
    for index, item in enumerate(problems):
        text = " ".join(
            [str(item.get("name", "")), *map(str, item.get("hosts", []) or []), *map(str, item.get("groups", []) or [])]
        )
        haystack = normalize(text)
        connectivity_subject = any(
            subject in q
            for subject in ("host", "dispositivo", "equipamento", "aparelho")
        )
        if "icmp" in terms and connectivity_subject:
            # Generic device nouns are ignored for ranking, but remain a semantic constraint:
            # internal Zabbix icmp-pinger utilization is not a host connectivity failure.
            if "pinger process" in haystack or "utilization of icmp" in haystack:
                continue
        if entity_terms and not any(entity in haystack for entity in entity_terms):
            continue
        score = sum(1 for term in terms if term and term in haystack)
        if score >= minimum_score:
            ranked.append((score, -index, item))
    ranked.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
    return [entry[2] for entry in ranked[:limit]]


def format_historical_triggers(events: list[dict[str, Any]], total_events: int, days: int, entity_label: str = "hosts", active_now: list[dict[str, Any]] | None = None) -> str:
    hosts = unique_affected_hosts(events)
    per_host: dict[str, int] = {}
    per_trigger: dict[str, int] = {}
    for event in events:
        for host in event.get("hosts", []) or []:
            per_host[str(host)] = per_host.get(str(host), 0) + 1
        name = str(event.get("name") or "Trigger sem nome")
        per_trigger[name] = per_trigger.get(name, 0) + 1
    ranked_hosts = sorted(per_host.items(), key=lambda item: (-item[1], item[0]))
    host_lines = [f"- {name}: {count} ocorrência(s)" for name, count in ranked_hosts[:15]]
    if len(ranked_hosts) > 15:
        host_lines.append(f"- ... e mais {len(ranked_hosts) - 15} switch(es), disponíveis nos gráficos e dados da execução.")
    trigger_lines = [f"- {name}: {count}" for name, count in sorted(per_trigger.items(), key=lambda item: (-item[1], item[0]))[:10]]
    if not events:
        return f"Não encontrei ocorrências de trigger para {entity_label} nos últimos {days} dias, entre {total_events} evento(s) consultado(s) no Zabbix."
    active_now = active_now or []
    active_hosts = unique_affected_hosts(active_now)
    critical_now = [item for item in active_now if int(item.get("severity", 0) or 0) >= 4]
    critical_hosts = unique_affected_hosts(critical_now)
    return (
        f"Nos últimos {days} dias, {len(hosts)} host(s) único(s) no escopo “{entity_label}” apresentaram {len(events)} ocorrência(s) de trigger. "
        f"O recorte foi aplicado sobre {total_events} evento(s) consultado(s) no Zabbix. "
        f"Neste momento, há {len(active_now)} problema(s) não resolvido(s) em {len(active_hosts)} host(s) desse escopo; "
        f"{len(critical_now)} são de severidade alta/desastre, afetando {len(critical_hosts)} host(s).\n\n"
        f"Ocorrências por host ({entity_label}):\n" + "\n".join(host_lines) +
        "\n\nPrincipais triggers:\n" + "\n".join(trigger_lines)
    )


def unique_affected_hosts(problems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for problem in problems:
        refs = problem.get("host_refs", []) or []
        if refs:
            for ref in refs:
                key = str(ref.get("hostid") or ref.get("name", "")).strip().lower()
                if not key:
                    continue
                current = unique.setdefault(key, {"hostid": ref.get("hostid"), "name": ref.get("name", ""), "groups": set()})
                current["groups"].update(ref.get("groups", []) or [])
        else:
            for name in problem.get("hosts", []) or []:
                key = str(name).strip().lower()
                if key:
                    unique.setdefault(key, {"hostid": None, "name": str(name), "groups": set(problem.get("groups", []) or [])})
    return [
        {"hostid": item["hostid"], "name": item["name"], "groups": sorted(item["groups"])}
        for item in sorted(unique.values(), key=lambda value: str(value["name"]).lower())
    ]


def format_related_problems(problems: list[dict[str, Any]], total_active: int, question: str = "") -> str:
    hosts = unique_affected_hosts(problems)
    lines = []
    for index, problem in enumerate(problems, start=1):
        affected = ", ".join(problem.get("hosts", []) or []) or "host não identificado"
        lines.append(f"{index}. [{problem.get('severity_label', 'N/A')}] {problem.get('name', 'Alarme sem nome')} — {affected}")
    if not problems:
        return f"Não encontrei alarmes ativos relacionados ao assunto entre os {total_active} problemas consultados no Zabbix."
    count_question = any(term in normalize(question) for term in ("quantos", "quantas", "quantidade", "total"))
    opening = (
        f"Há {len(hosts)} host(s) único(s) com {len(problems)} alarme(s) relacionado(s)"
        if count_question else f"Encontrei {len(problems)} alarme(s) relacionado(s), afetando {len(hosts)} host(s) único(s)"
    )
    host_lines = [
        f"- {host['name']}" + (f" (grupos: {', '.join(host['groups'])})" if host["groups"] else "")
        for host in hosts
    ]
    return (
        opening + ", "
        f"entre {total_active} problema(s) ativo(s) consultado(s) no Zabbix.\n\n"
        + "\n".join(lines)
        + (f"\n\nHosts únicos afetados:\n" + "\n".join(host_lines) if hosts else "")
    )
