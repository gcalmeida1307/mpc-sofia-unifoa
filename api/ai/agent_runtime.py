from __future__ import annotations

from typing import Any


AGENT_CATALOG: list[dict[str, Any]] = [
    {
        "name": "Operations Agent",
        "key": "operations",
        "objectives": ["stabilize service", "prioritize incidents", "coordinate remediation"],
        "playbook": ["triage", "evidence collection", "action recommendation"],
        "memory_scope": "cross-domain incidents",
        "tool_budget": {"max_tools": 6, "max_runtime_s": 25},
        "critic_focus": "operational risk and rollback safety",
    },
    {
        "name": "Infrastructure Agent",
        "key": "infrastructure",
        "objectives": ["host health", "availability", "topology anomalies"],
        "playbook": ["zabbix trend review", "host grouping", "root-cause narrowing"],
        "memory_scope": "infra incidents",
        "tool_budget": {"max_tools": 5, "max_runtime_s": 20},
        "critic_focus": "evidence completeness",
    },
    {
        "name": "Security Agent",
        "key": "security",
        "objectives": ["detect auth/network threats", "reduce blast radius"],
        "playbook": ["alert correlation", "risk scoring", "containment recommendations"],
        "memory_scope": "security events",
        "tool_budget": {"max_tools": 4, "max_runtime_s": 20},
        "critic_focus": "false positive reduction",
    },
    {
        "name": "Database Agent",
        "key": "database",
        "objectives": ["query health", "storage pressure", "replication"],
        "playbook": ["capacity check", "latency check", "index guidance"],
        "memory_scope": "database operations",
        "tool_budget": {"max_tools": 4, "max_runtime_s": 20},
        "critic_focus": "data integrity risk",
    },
    {
        "name": "Network Agent",
        "key": "network",
        "objectives": ["link stability", "loop detection", "edge performance"],
        "playbook": ["hypothesis generation", "packet-symptom correlation", "segment impact"],
        "memory_scope": "network incidents",
        "tool_budget": {"max_tools": 5, "max_runtime_s": 20},
        "critic_focus": "root-cause precision",
    },
    {
        "name": "Developer Agent",
        "key": "developer",
        "objectives": ["delivery velocity", "service debug", "tooling"],
        "playbook": ["trace review", "dependency checks", "implementation notes"],
        "memory_scope": "engineering workflow",
        "tool_budget": {"max_tools": 4, "max_runtime_s": 15},
        "critic_focus": "implementation feasibility",
    },
    {
        "name": "Learning Agent",
        "key": "learning",
        "objectives": ["extract recurring patterns", "promote reusable insights"],
        "playbook": ["cluster incidents", "promote insight", "update weights"],
        "memory_scope": "cross-session knowledge",
        "tool_budget": {"max_tools": 4, "max_runtime_s": 15},
        "critic_focus": "knowledge reuse rate",
    },
    {
        "name": "Automation Agent",
        "key": "automation",
        "objectives": ["orchestrate workflows", "auto-investigation triggers"],
        "playbook": ["workflow dispatch", "handoff", "verification callback"],
        "memory_scope": "workflow outcomes",
        "tool_budget": {"max_tools": 4, "max_runtime_s": 15},
        "critic_focus": "execution reliability",
    },
]


class AgentRuntime:
    def resolve(self, question: str, plan: dict[str, Any]) -> dict[str, Any]:
        intent = str(plan.get("intent", "")).lower()
        semantic = plan.get("semantic_query", {}) if isinstance(plan.get("semantic_query"), dict) else {}
        domain = str(semantic.get("domain") or plan.get("domain") or "general").lower()

        if domain == "security":
            return self._by_key("security")
        if domain == "network":
            return self._by_key("network")
        if domain == "database":
            return self._by_key("database")
        if domain == "infrastructure":
            return self._by_key("infrastructure")
        if domain == "automation" or intent == "workflow_lookup":
            return self._by_key("automation")
        if any(token in intent for token in ["incident", "host", "docker"]):
            return self._by_key("operations")
        return self._by_key("developer")

    def status(self) -> dict[str, Any]:
        return {
            "count": len(AGENT_CATALOG),
            "agents": AGENT_CATALOG,
        }

    @staticmethod
    def _by_key(key: str) -> dict[str, Any]:
        for agent in AGENT_CATALOG:
            if agent.get("key") == key:
                return agent
        return AGENT_CATALOG[0]


agent_runtime = AgentRuntime()
