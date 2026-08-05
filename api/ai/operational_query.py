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


def related_problems(question: str, problems: list[dict[str, Any]], limit: int = 500) -> list[dict[str, Any]]:
    q = normalize(question)
    ignored = {
        "qual", "quais", "quantos", "quantas", "tenho", "tem", "estao", "nao", "para", "por", "que",
        "uma", "uns", "das", "dos", "de", "do", "da", "em", "no", "na", "meu", "minha", "sobre",
        "todos", "todas", "alerta", "alertas", "alarme", "alarmes", "problema", "problemas", "respondem",
        "zabbix", "host", "hosts", "ativo", "ativos",
        "com", "sem", "pelo", "pela", "pelos", "pelas",
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
        if "icmp" in terms and "host" not in terms and "hosts" in normalize(question):
            # "host/hosts" is ignored for ranking, but remains a semantic constraint:
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
