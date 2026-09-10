"""Bounded agent/harness loop for retrieval decisions.

This is orchestration control, not chain-of-thought. It records observable
decisions so a failed answer explains whether the issue was routing, corpus,
evidence or generation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .policies import ModulePolicy
from .retrieval import RetrievalResult


@dataclass(frozen=True)
class HarnessRun:
    result: RetrievalResult
    steps: tuple[dict[str, object], ...]
    attempts: int
    decision: str


Retriever = Callable[[str, int, bool], RetrievalResult]


def _has_authoritative_jurisprudence_source(result: RetrievalResult) -> bool:
    """Return whether a result adds a first-party legal research source.

    A retry that was explicitly asked to include jurisprudence may discover an
    official STJ/STF/Planalto source after the first pass.  The retry must not
    be discarded solely because its average score is a little lower: the
    source is complementary evidence about the jurisprudential search and is
    not allowed to replace the named primary documents.
    """
    return any(
        any(marker in source.casefold() for marker in ("stj", "stf", "planalto"))
        for source in result.sources
    )


def run_retrieval_harness(
    root: Path,
    module_id: str,
    question: str,
    policy: ModulePolicy,
    retriever: Retriever,
    limit: int = 6,
) -> HarnessRun:
    """Plan → retrieve → reflect → retrieve once when evidence is weak.

    The loop is bounded to two retrieval attempts. It never silently switches
    modules and never calls an external provider; provider routing remains the
    responsibility of the provider policy after this gate.
    """
    del root, module_id
    steps: list[dict[str, object]] = [{"stage": "plan", "status": "complete", "attempt": 1}]
    first = retriever(question, limit, False)
    steps.append({"stage": "retrieve", "status": "complete" if first.has_quality_evidence else "incomplete", "accepted": len(first.evidence), "rejected": len(first.rejected_evidence), "conflicts": len(first.conflicts), "missing_sources": list(first.missing_sources), "attempt": 1})
    if first.has_quality_evidence and first.judge_confidence >= max(0.30, policy.min_evidence_score * 0.90) and not first.conflicts:
        steps.append({"stage": "reflect", "status": "sufficient", "decision": "reason_with_accepted_evidence", "attempt": 1})
        return HarnessRun(first, tuple(steps), 1, "reason_with_accepted_evidence")
    steps.append({"stage": "reflect", "status": "needs_more_evidence", "decision": "broaden_same_module_sources", "attempt": 1})
    second = retriever(question, max(limit * 2, 8), True)
    steps.append({"stage": "retrieve", "status": "complete" if second.has_quality_evidence else "incomplete", "accepted": len(second.evidence), "rejected": len(second.rejected_evidence), "conflicts": len(second.conflicts), "missing_sources": list(second.missing_sources), "attempt": 2})
    jurisprudence_requested = any(
        marker in question.casefold()
        for marker in ("jurisprud", "precedent", "link")
    )
    second_adds_authoritative_jurisprudence = (
        jurisprudence_requested
        and _has_authoritative_jurisprudence_source(second)
        and not _has_authoritative_jurisprudence_source(first)
    )
    if second.evidence and (
        not first.has_quality_evidence
        or second.judge_confidence >= first.judge_confidence
        or second_adds_authoritative_jurisprudence
    ):
        steps.append({"stage": "reflect", "status": "sufficient" if not second.conflicts else "review_required", "decision": "reason_with_second_pass", "attempt": 2})
        return HarnessRun(second, tuple(steps), 2, "reason_with_second_pass")
    steps.append({"stage": "reflect", "status": "insufficient", "decision": "report_evidence_gap", "attempt": 2})
    return HarnessRun(first, tuple(steps), 2, "report_evidence_gap")
