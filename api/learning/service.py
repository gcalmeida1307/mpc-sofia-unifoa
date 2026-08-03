from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha1
from typing import Any

from services.postgres_store import postgres_store
from context.infrastructure import snapshot_service
from services.knowledge import search_knowledge


class LearningService:
    def _problem_family(self, name: str, hosts: list[str]) -> str:
        text = f"{name} {' '.join(hosts)}".lower()
        if any(token in text for token in ["switch", "ethernet", "link down", "speed", "duplex"]):
            return "network-switch-l2"
        if any(token in text for token in ["windows", "disk", "memory", "cpu", "zabbix agent"]):
            return "windows-host-health"
        if any(token in text for token in ["fortigate", "vpn", "firewall"]):
            return "network-edge-security"
        if any(token in text for token in ["airtime", "wifi", "ap", "wireless"]):
            return "wireless-access"
        return "general"

    def _signature(self, family: str, summary: dict[str, Any]) -> str:
        raw = f"{family}:{summary.get('problem_count', 0)}:{summary.get('host_count', 0)}:{summary.get('severity_3', 0)}:{summary.get('severity_2', 0)}:{summary.get('severity_1', 0)}"
        return sha1(raw.encode("utf-8")).hexdigest()

    def learn(self, question: str | None = None) -> dict[str, Any]:
        snapshot = snapshot_service.get(force_refresh=True)
        zabbix = snapshot.get("zabbix", {}) if isinstance(snapshot, dict) else {}
        problems = zabbix.get("problems", []) if isinstance(zabbix, dict) else []
        summary = zabbix.get("problem_summary", {}) if isinstance(zabbix, dict) else {}
        knowledge_hits = search_knowledge(question or "") if question else {"results": []}

        family_counter: Counter[str] = Counter()
        family_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
        host_counter: Counter[str] = Counter()

        for item in problems:
            hosts = item.get("hosts", []) if isinstance(item, dict) else []
            family = self._problem_family(item.get("name", ""), hosts)
            family_counter[family] += 1
            family_examples[family].append({
                "name": item.get("name", ""),
                "severity": item.get("severity_label", item.get("severity", "")),
                "hosts": hosts,
            })
            for host in hosts:
                if host:
                    host_counter[host] += 1

        patterns = []
        for family, count in family_counter.most_common():
            if count == 0:
                continue
            if family == "network-switch-l2" and count >= 5:
                patterns.append({
                    "family": family,
                    "signal": "Recurring layer-2 / switch issues",
                    "count": count,
                    "insight": "Há recorrência de eventos de switch/link/speed. Vale verificar uplinks, VLANs e cabos antes de atuar em cima do sintoma.",
                })
            elif family == "wireless-access" and count >= 3:
                patterns.append({
                    "family": family,
                    "signal": "Recurring wireless/access-point issues",
                    "count": count,
                    "insight": "Há recorrência em wireless/AP. O padrão sugere checagem de interferência, airtime e cobertura.",
                })
            elif family == "windows-host-health" and count >= 3:
                patterns.append({
                    "family": family,
                    "signal": "Recurring Windows health issues",
                    "count": count,
                    "insight": "Há recorrência em Windows. Sugere validar espaço em disco, services e agent health.",
                })
            elif family == "network-edge-security" and count >= 3:
                patterns.append({
                    "family": family,
                    "signal": "Recurring edge/security connectivity issues",
                    "count": count,
                    "insight": "Há recorrência de VPN/firewall. Sugere validar túneis, sessões e logs de borda.",
                })

        top_hosts = [
            {"host": host, "occurrences": count}
            for host, count in host_counter.most_common(10)
        ]

        insights = {
            "summary": {
                "hosts": zabbix.get("host_count", 0),
                "problems": len(problems),
                "containers": len(snapshot.get("docker", {}).get("containers", [])) if isinstance(snapshot.get("docker", {}), dict) else 0,
            },
            "patterns": patterns,
            "top_hosts": top_hosts,
            "knowledge_hits": knowledge_hits.get("results", [])[:3],
            "examples": {family: family_examples[family][:3] for family in family_examples},
        }

        signature = self._signature(patterns[0]["family"] if patterns else "general", {
            "problem_count": len(problems),
            "host_count": zabbix.get("host_count", 0),
            "severity_3": summary.get("severity_buckets", {}).get("3", 0) if isinstance(summary.get("severity_buckets", {}), dict) else 0,
            "severity_2": summary.get("severity_buckets", {}).get("2", 0) if isinstance(summary.get("severity_buckets", {}), dict) else 0,
            "severity_1": summary.get("severity_buckets", {}).get("1", 0) if isinstance(summary.get("severity_buckets", {}), dict) else 0,
        })
        headline = patterns[0]["insight"] if patterns else "Snapshot atualizado sem recorrências fortes detectadas."
        postgres_store.save_insight(signature, "infrastructure-pattern", headline, insights)
        return insights

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return postgres_store.get_recent_insights(limit=limit)


learning_service = LearningService()
