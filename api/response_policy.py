"""Single evidence-to-generation policy for the SOFIA CORE.

The policy decides *which boundary* the answer pipeline is in.  It does not
know legal, medical, Zabbix or other topic rules.  Domain packages decide what
counts as relevant evidence; this module only prevents a provider from being
used as if it had local evidence when the Evidence Judge found none.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .policies import ModulePolicy
from .privacy import external_generation_may_be_used
from .retrieval import RetrievalResult


@dataclass(frozen=True)
class ResponsePolicy:
    """Observable response boundary selected after retrieval."""

    route: str
    use_local_evidence: bool
    allow_external_assist: bool
    reason: str


def should_enqueue_unanswered_topic(
    *,
    evidence_found: bool,
    context_package: dict[str, Any],
    enabled: bool = True,
) -> bool:
    """Return whether a turn belongs in the optional learning queue.

    The queue is for unresolved documentary demand, not for conversation.  It
    is deliberately based on the already selected execution contract so this
    helper never runs a second router or inspects topic-specific words.
    """

    if not enabled or evidence_found:
        return False
    if not bool(context_package.get("retrieval_required")):
        return False
    return str(context_package.get("task_route", "")) not in {"conversation", "writing"}


def choose_response_policy(
    result: RetrievalResult,
    *,
    query_plan: Any,
    policy: ModulePolicy,
    provider: str,
    external_allowed: bool | None,
) -> ResponsePolicy:
    """Choose grounded synthesis or a clearly labelled no-evidence fallback.

    This is intentionally the only generic branch between retrieval and
    generation.  A named-source/comparison contract cannot be completed by a
    cloud model when the local source is missing.  A normal domain question
    may receive a general, explicitly ungrounded answer when the deployment
    authorizes it.  Clinical modules remain local-first through their policy.
    """

    if result.has_quality_evidence:
        return ResponsePolicy(
            route="grounded",
            use_local_evidence=True,
            allow_external_assist=False,
            reason="evidência local aprovada pelo Evidence Judge",
        )

    strategy = str(getattr(query_plan, "strategy", "FACT_LOOKUP"))
    local_contract = policy.high_risk or bool(result.required_sources) or strategy in {
        "DOCUMENT_SUMMARY",
        "MULTI_DOCUMENT_SYNTHESIS",
        "CONCEPT_COMPARISON",
        "MULTI_HOP",
        "RCA_INVESTIGATION",
    }
    # The question may explicitly choose a local provider, but it still must
    # not fabricate a documentary answer.  The external fallback is a
    # generation route, never an evidence route.
    external_opt_in = external_generation_may_be_used(provider, external_allowed)
    provider_can_assist = provider in {"auto", "ollama", "openai", "gemini", "claude"}
    allow_assist = not local_contract and provider_can_assist and (
        provider in {"auto", "ollama"} or external_opt_in
    )
    if allow_assist:
        return ResponsePolicy(
            route="external_assist",
            use_local_evidence=False,
            allow_external_assist=True,
            reason="a base local não confirmou a pergunta; orientação geral isolada",
        )
    return ResponsePolicy(
        route="evidence_gap",
        use_local_evidence=False,
        allow_external_assist=False,
        reason="a base local não confirmou a pergunta e o contrato exige evidência local",
    )
