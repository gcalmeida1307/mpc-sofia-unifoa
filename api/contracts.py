"""Small, serializable contracts shared by intelligence subsystems.

These are intentionally independent of FastAPI and provider SDKs.  That keeps
the CORE testable and prevents a provider or domain from leaking into routes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PIPELINE_STAGES = (
    "RECEIVED", "EXTRACTING", "OCR", "QUALITY_CHECK", "NORMALIZING",
    "MARKDOWN_READY", "UNDERSTANDING", "CHUNKING", "EMBEDDING", "RELATING",
    "INDEXING", "VALIDATING", "READY",
)


@dataclass(frozen=True)
class EvidenceContract:
    source: str
    ordinal: int
    score: float
    lexical_score: float
    semantic_score: float
    coverage: float
    accepted: bool
    reason: str = ""
    authority_score: float = 0.0
    freshness_score: float = 0.0
    provenance_score: float = 0.0
    support_score: float = 0.0
    contradiction_score: float = 0.0


@dataclass(frozen=True)
class ContextPackage:
    question: str
    domain: str
    intent: str
    complexity: str
    risk: str
    conversation_context: list[dict[str, str]] = field(default_factory=list)
    accepted_evidence: list[EvidenceContract] = field(default_factory=list)
    rejected_evidence: list[EvidenceContract] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)
    domain_policy: dict[str, Any] = field(default_factory=dict)
    expected_response_type: str = "structured"

    def public_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationResult:
    status: str
    confidence: float
    unsupported_claims: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolContract:
    name: str
    domain: str | None
    description: str
    required_capability: str
    timeout_seconds: float
    audit_event: str
    allowlist: tuple[str, ...] = ()
