from __future__ import annotations

from typing import Any


class HypothesisEngine:
    _TEMPLATES: dict[str, list[dict[str, Any]]] = {
        "network": [
            {
                "id": "loop_stp",
                "title": "Loop STP",
                "tokens": ["loop", "stp", "broadcast", "storm"],
                "evidence_expected": ["increase in switch/link alerts", "high broadcast related triggers"],
                "verification_tools": ["zabbix.list_problems", "knowledge.search"],
                "cost_to_verify": "medium",
            },
            {
                "id": "cpu_high",
                "title": "CPU alta em equipamento de rede",
                "tokens": ["cpu", "high cpu", "processor"],
                "evidence_expected": ["cpu triggers in top hosts", "same device recurring in incidents"],
                "verification_tools": ["zabbix.list_problems", "learning.insights"],
                "cost_to_verify": "low",
            },
            {
                "id": "link_saturation",
                "title": "Saturacao de link",
                "tokens": ["latency", "throughput", "link", "saturation", "speed"],
                "evidence_expected": ["latency and packet issues grouped by same uplink"],
                "verification_tools": ["zabbix.list_problems", "knowledge.search"],
                "cost_to_verify": "medium",
            },
            {
                "id": "crc_errors",
                "title": "Erros CRC/camada fisica",
                "tokens": ["crc", "duplex", "ethernet", "interface"],
                "evidence_expected": ["interface error triggers and recurring host ports"],
                "verification_tools": ["zabbix.list_problems"],
                "cost_to_verify": "low",
            },
            {
                "id": "broadcast_storm",
                "title": "Broadcast storm",
                "tokens": ["broadcast", "storm", "flood", "arp"],
                "evidence_expected": ["simultaneous alerts in same network segment"],
                "verification_tools": ["zabbix.list_problems", "learning.insights"],
                "cost_to_verify": "high",
            },
        ],
        "security": [
            {
                "id": "vpn_instability",
                "title": "Instabilidade de VPN/firewall",
                "tokens": ["vpn", "firewall", "tunnel", "ssl"],
                "evidence_expected": ["clustered edge-security alerts"],
                "verification_tools": ["zabbix.list_problems", "knowledge.search"],
                "cost_to_verify": "medium",
            },
            {
                "id": "auth_failures",
                "title": "Falhas de autenticacao",
                "tokens": ["auth", "login", "unauthorized", "bruteforce"],
                "evidence_expected": ["recurring authentication failures in same period"],
                "verification_tools": ["zabbix.list_problems", "learning.insights"],
                "cost_to_verify": "low",
            },
        ],
        "capacity": [
            {
                "id": "memory_pressure",
                "title": "Pressao de memoria",
                "tokens": ["memory", "ram", "oom"],
                "evidence_expected": ["memory alerts in critical services"],
                "verification_tools": ["zabbix.list_problems"],
                "cost_to_verify": "low",
            },
            {
                "id": "disk_pressure",
                "title": "Pressao de disco",
                "tokens": ["disk", "storage", "filesystem", "iops"],
                "evidence_expected": ["disk and latency alerts in same hosts"],
                "verification_tools": ["zabbix.list_problems", "knowledge.search"],
                "cost_to_verify": "low",
            },
            {
                "id": "cpu_contention",
                "title": "Contencao de CPU",
                "tokens": ["cpu", "load", "steal", "saturation"],
                "evidence_expected": ["high cpu and queue related incidents"],
                "verification_tools": ["zabbix.list_problems", "learning.insights"],
                "cost_to_verify": "low",
            },
        ],
        "general": [
            {
                "id": "insufficient_evidence",
                "title": "Evidencia insuficiente",
                "tokens": [],
                "evidence_expected": ["collect additional telemetry before action"],
                "verification_tools": ["registry.snapshot", "knowledge.search"],
                "cost_to_verify": "low",
            }
        ],
    }

    def build(self, question: str, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        domain = self._infer_domain(question=question, plan=plan)
        templates = self._TEMPLATES.get(domain, self._TEMPLATES["general"])

        problems = context.get("tools", {}).get("zabbix.list_problems", {}).get("problems", [])
        if not isinstance(problems, list):
            problems = []

        corpus = " ".join(
            [
                str(question).lower(),
                " ".join(str(item.get("name", "")).lower() for item in problems if isinstance(item, dict)),
            ]
        )

        hypotheses: list[dict[str, Any]] = []
        for item in templates:
            score = self._score(item.get("tokens", []), corpus)
            confidence = round(min(0.95, 0.35 + score), 3)
            observed = [token for token in item.get("tokens", []) if token and token in corpus]
            hypotheses.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "confidence": confidence,
                    "cost_to_verify": item.get("cost_to_verify", "medium"),
                    "evidence_expected": item.get("evidence_expected", []),
                    "verification_tools": item.get("verification_tools", []),
                    "observed_signals": observed,
                    "missing_evidence": len(observed) == 0,
                    "status": "candidate",
                }
            )

        hypotheses.sort(key=lambda row: row.get("confidence", 0.0), reverse=True)
        selected = hypotheses[0] if hypotheses else None

        return {
            "symptom": question,
            "domain": domain,
            "hypotheses": hypotheses,
            "selected_hypothesis": selected.get("id") if selected else None,
            "confidence": selected.get("confidence", 0.0) if selected else 0.0,
            "analysis_mode": "hypothesis_engine_v1",
        }

    @staticmethod
    def _score(tokens: list[str], corpus: str) -> float:
        if not tokens:
            return 0.0
        matched = sum(1 for token in tokens if token in corpus)
        ratio = matched / max(len(tokens), 1)
        return ratio * 0.6

    @staticmethod
    def _infer_domain(question: str, plan: dict[str, Any]) -> str:
        semantic = plan.get("semantic_query", {}) if isinstance(plan.get("semantic_query"), dict) else {}
        semantic_domain = str(semantic.get("domain") or plan.get("domain") or "").lower()
        if semantic_domain in {"network", "security"}:
            return semantic_domain
        if semantic_domain in {"capacity", "database", "infrastructure"}:
            return "capacity" if str(semantic.get("metric", "none")) in {"cpu", "memory", "disk", "latency"} else "general"
        q = question.lower()
        intent = str(plan.get("intent", "")).lower()

        if any(term in q for term in ["vpn", "firewall", "auth", "login", "security"]) or "security" in intent:
            return "security"
        if any(term in q for term in ["cpu", "memory", "disk", "latency", "capacity"]) or "capacity" in intent:
            return "capacity"
        if any(term in q for term in ["switch", "stp", "link", "network", "broadcast", "crc"]):
            return "network"
        if any(term in q for term in ["zabbix", "host", "problema", "incident"]):
            return "network"
        return "general"


hypothesis_engine = HypothesisEngine()
