from __future__ import annotations

from collections import Counter
from typing import Any


def unique_affected_hosts(problems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for problem in problems:
        refs = problem.get("host_refs", []) or []
        if refs:
            for ref in refs:
                key = str(ref.get("hostid") or ref.get("name", "")).strip().lower()
                if not key:
                    continue
                current = unique.setdefault(key, {"hostid":ref.get("hostid"),"name":ref.get("name", ""),"groups":set()})
                current["groups"].update(ref.get("groups", []) or [])
        else:
            for name in problem.get("hosts", []) or []:
                key = str(name).strip().lower()
                if key:
                    unique.setdefault(key, {"hostid":None,"name":str(name),"groups":set(problem.get("groups", []) or [])})
    return [{"hostid":item["hostid"],"name":item["name"],"groups":sorted(item["groups"])} for item in sorted(unique.values(), key=lambda value:str(value["name"]).lower())]


def distributions(problems: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    severity = Counter(str(item.get("severity_label") or "Não classificado") for item in problems)
    groups = Counter(group for item in problems for group in (item.get("groups") or []))
    hosts = Counter(str(host) for item in problems for host in (item.get("hosts") or []) if host)
    return {
        "severity_distribution":[{"label":key,"value":value} for key,value in severity.most_common()],
        "group_distribution":[{"label":key,"value":value} for key,value in groups.most_common(8)],
        "host_distribution":[{"label":key,"value":value} for key,value in hosts.most_common(12)],
    }
