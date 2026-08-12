from __future__ import annotations

from hashlib import sha256
from typing import Any

from ai.hypothesis import hypothesis_engine
from context.infrastructure import snapshot_service
from core.event_bus import event_bus
from services.postgres_store import postgres_store


class AutonomousInvestigator:
    def __init__(self):
        self._seen_signatures: set[str] = set()

    def run_cycle(self) -> dict[str, Any]:
        snapshot = snapshot_service.get(force_refresh=False)
        context = self._context_from_snapshot(snapshot)

        candidates = [
            self._infra_watcher(context),
            self._security_watcher(context),
            self._capacity_watcher(context),
        ]
        investigations: list[dict[str, Any]] = []

        for candidate in candidates:
            if not candidate:
                continue
            signature = self._signature(candidate)
            if signature in self._seen_signatures:
                continue

            hypothesis = hypothesis_engine.build(
                question=candidate["symptom"],
                plan={"intent": "incident_analysis", "tools": ["zabbix.list_problems", "learning.insights"]},
                context=context,
            )
            record = {
                "watcher": candidate["watcher"],
                "title": candidate["title"],
                "severity": candidate["severity"],
                "status": "open",
                "summary": candidate["summary"],
                "hypothesis": hypothesis,
                "evidence": candidate["evidence"],
                "metadata": {"signature": signature},
            }

            postgres_store.save_autonomous_investigation(**record)
            postgres_store.save_insight(
                signature=signature,
                kind=f"autonomous.{candidate['watcher']}",
                summary=candidate["summary"],
                payload={
                    "title": candidate["title"],
                    "severity": candidate["severity"],
                    "hypothesis": hypothesis,
                    "evidence": candidate["evidence"],
                },
            )
            event_bus.publish_sync(
                "investigation.created",
                {
                    "watcher": candidate["watcher"],
                    "title": candidate["title"],
                    "severity": candidate["severity"],
                    "summary": candidate["summary"],
                },
            )

            self._seen_signatures.add(signature)
            investigations.append(record)

        if len(self._seen_signatures) > 500:
            self._seen_signatures = set(list(self._seen_signatures)[-250:])

        return {
            "created": len(investigations),
            "investigations": investigations,
        }

    @staticmethod
    def _context_from_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
        zabbix = snapshot.get("zabbix", {}) if isinstance(snapshot.get("zabbix", {}), dict) else {}
        problems = zabbix.get("problems", []) if isinstance(zabbix.get("problems", []), list) else []
        return {
            "tools": {
                "zabbix.list_problems": {
                    "problems": problems,
                    "summary": zabbix.get("problem_summary", {}),
                }
            },
            "summary": {
                "hosts": zabbix.get("host_count", 0),
                "problems": len(problems),
            },
        }

    @staticmethod
    def _infra_watcher(context: dict[str, Any]) -> dict[str, Any] | None:
        problems = context.get("tools", {}).get("zabbix.list_problems", {}).get("problems", [])
        count = len(problems) if isinstance(problems, list) else 0
        if count < 20:
            return None
        evidence = [{"kind": "problem_count", "value": count}]
        return {
            "watcher": "infra",
            "title": "Infra anomaly detected",
            "severity": "high" if count >= 40 else "medium",
            "symptom": "Volume elevado de incidentes de infraestrutura",
            "summary": f"SOFIA detectou aumento de incidentes de infraestrutura: {count} eventos ativos.",
            "evidence": evidence,
        }

    @staticmethod
    def _security_watcher(context: dict[str, Any]) -> dict[str, Any] | None:
        problems = context.get("tools", {}).get("zabbix.list_problems", {}).get("problems", [])
        if not isinstance(problems, list):
            return None
        tokens = ["vpn", "firewall", "auth", "login", "ssl", "cert"]
        security_hits = 0
        for item in problems:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).lower()
            if any(token in name for token in tokens):
                security_hits += 1
        if security_hits < 5:
            return None
        return {
            "watcher": "security",
            "title": "Security pattern detected",
            "severity": "high" if security_hits >= 10 else "medium",
            "symptom": "Aumento de eventos de seguranca e autenticacao",
            "summary": f"SOFIA detectou {security_hits} eventos relacionados a seguranca/autenticacao no ciclo atual.",
            "evidence": [{"kind": "security_hits", "value": security_hits}],
        }

    @staticmethod
    def _capacity_watcher(context: dict[str, Any]) -> dict[str, Any] | None:
        problems = context.get("tools", {}).get("zabbix.list_problems", {}).get("problems", [])
        if not isinstance(problems, list):
            return None
        tokens = ["cpu", "memory", "disk", "latency", "saturation", "load"]
        capacity_hits = 0
        for item in problems:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).lower()
            if any(token in name for token in tokens):
                capacity_hits += 1
        if capacity_hits < 6:
            return None
        return {
            "watcher": "capacity",
            "title": "Capacity pressure detected",
            "severity": "high" if capacity_hits >= 12 else "medium",
            "symptom": "Pressao de capacidade em servicos monitorados",
            "summary": f"SOFIA detectou {capacity_hits} eventos de capacidade (CPU/memoria/disco/latencia).",
            "evidence": [{"kind": "capacity_hits", "value": capacity_hits}],
        }

    @staticmethod
    def _signature(candidate: dict[str, Any]) -> str:
        base = f"{candidate.get('watcher')}|{candidate.get('title')}|{candidate.get('severity')}|{candidate.get('summary')}"
        return sha256(base.encode("utf-8")).hexdigest()


autonomous_investigator = AutonomousInvestigator()
