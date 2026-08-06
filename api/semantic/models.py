from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SemanticIntent = Literal[
    "general_chat", "knowledge_lookup", "host_count", "active_trigger_summary",
    "historical_trigger_summary", "incident_analysis", "network_investigation",
    "security_investigation", "capacity_investigation", "docker_observe",
    "docker_action", "marketplace", "workflow_lookup", "out_of_scope",
]


class SemanticTimeRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    days: int | None = Field(default=None, ge=1, le=90)
    start: str | None = None
    end: str | None = None


class SemanticQuery(BaseModel):
    """Canonical, validated contract between language and execution layers."""

    model_config = ConfigDict(extra="forbid")

    intent: SemanticIntent
    domain: Literal["general", "network", "infrastructure", "security", "database", "automation", "development"] = "general"
    source: Literal["zabbix", "knowledge", "docker", "marketplace", "workflow", "none"] = "none"
    entity_type: Literal["host", "switch", "server", "access_point", "firewall", "router", "ups", "container", "document", "unknown"] = "unknown"
    entity_name: str | None = Field(default=None, max_length=120)
    time_range: SemanticTimeRange | None = None
    metric: Literal["trigger_count", "host_count", "active_problems", "availability", "cpu", "memory", "disk", "latency", "none"] = "none"
    state: Literal["active", "historical", "current", "conceptual", "unknown"] = "unknown"
    group_by: Literal["host", "trigger", "severity", "group", "time", "none"] = "none"
    ambiguities: list[str] = Field(default_factory=list, max_length=8)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_clarification: bool = False
    interpretation_source: Literal["anthropic", "ollama", "deterministic", "unknown"] = "unknown"

    @field_validator("entity_name")
    @classmethod
    def safe_entity_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ .'")
        if any(char not in allowed for char in value):
            raise ValueError("entity_name contains unsupported characters")
        return value

    def logical_signature(self) -> tuple:
        return (
            self.intent, self.domain, self.source, self.entity_type, self.entity_name,
            self.time_range.days if self.time_range else None, self.metric, self.state, self.group_by,
        )
