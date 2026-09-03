"""Formal evidence judge between retrieval and reasoning."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .query_analysis import normalize

if TYPE_CHECKING:
    from .policies import ModulePolicy
    from .retrieval import Evidence


@dataclass(frozen=True)
class EvidenceDecision:
    accepted: tuple[Evidence, ...]
    rejected: tuple[Evidence, ...]
    conflicts: tuple[dict[str, Any], ...]


def _authority(path: Path) -> float:
    name = normalize(path.name)
    if path.parent.name.casefold() == "links":
        if any(marker in name for marker in ("gov-br", "planalto", "stf", "stj", "zabbix-com", "who-int", "cdc")):
            return 0.92
        return 0.72
    if path.suffix.casefold() in {".pdf", ".docx", ".xlsx"}:
        return 0.86
    return 0.78


def _freshness(path: Path) -> float:
    # Freshness is intentionally neutral until a source registry supplies a
    # publication/checked timestamp. A newer file is not automatically more
    # authoritative than an official older norm.
    del path
    return 0.75


def _provenance(path: Path) -> float:
    return 0.92 if path.exists() and path.name != ".gitkeep" else 0.25


def _negated_overlap(left: str, right: str) -> bool:
    left_norm, right_norm = f" {normalize(left)} ", f" {normalize(right)} "
    negation = (" nao ", " nunca ", " impede ", " proib", " jamais ")
    if not any(marker in left_norm or marker in right_norm for marker in negation):
        return False
    left_tokens = set(re.findall(r"[\w]+", left_norm)) - {"nao", "não"}
    right_tokens = set(re.findall(r"[\w]+", right_norm)) - {"nao", "não"}
    return len(left_tokens & right_tokens) >= 4


def judge_candidates(question: str, module_id: str, policy: ModulePolicy, candidates: Iterable[Evidence]) -> EvidenceDecision:
    """Score relevance, authority, freshness, provenance and support.

    This function does not call an LLM and never exposes a chain of thought.
    It returns explicit rejected/conflicting evidence so the reasoner and the
    admin observability surface can explain why a passage was not used.
    """
    terms = {
        term
        for term in re.findall(r"[\wÀ-ÿ]{4,}", normalize(question))
        if term not in {"como", "qual", "quais", "sobre", "para", "documento", "arquivo"}
    }
    accepted: list[Evidence] = []
    rejected: list[Evidence] = []
    conflicts: list[dict[str, Any]] = []
    threshold = max(0.18, min(0.62, float(policy.min_evidence_score) * 0.72))
    for candidate in candidates:
        text = normalize(candidate.chunk.text)
        matched = sum(1 for term in terms if term in text)
        question_coverage = matched / max(1, len(terms))
        authority = _authority(candidate.chunk.path)
        freshness = _freshness(candidate.chunk.path)
        provenance = _provenance(candidate.chunk.path)
        support = max(float(candidate.coverage), question_coverage)
        judge_score = 0.42 * float(candidate.score) + 0.16 * authority + 0.12 * freshness + 0.14 * provenance + 0.16 * support
        enriched = candidate.__class__(
            candidate.chunk,
            round(min(1.0, judge_score), 4),
            candidate.lexical_score,
            candidate.semantic_score,
            candidate.coverage,
            candidate.bm25_score,
            round(authority, 4),
            round(freshness, 4),
            round(provenance, 4),
            round(support, 4),
            0.0,
            True,
            "",
        )
        if judge_score >= threshold and (candidate.coverage >= 0.08 or candidate.score >= 0.25):
            accepted.append(enriched)
        else:
            rejected.append(
                enriched.__class__(
                    enriched.chunk,
                    enriched.score,
                    enriched.lexical_score,
                    enriched.semantic_score,
                    enriched.coverage,
                    enriched.bm25_score,
                    enriched.authority_score,
                    enriched.freshness_score,
                    enriched.provenance_score,
                    enriched.support_score,
                    enriched.contradiction_score,
                    False,
                    "não atingiu relevância, suporte ou proveniência mínimos",
                )
            )
    for index, left in enumerate(accepted):
        for right in accepted[index + 1 :]:
            if left.chunk.path.name != right.chunk.path.name and _negated_overlap(left.chunk.text, right.chunk.text):
                conflicts.append({"left_source": left.chunk.path.name, "right_source": right.chunk.path.name, "type": "textual_tension", "status": "needs_review"})
    if module_id == "medicina" and conflicts:
        accepted = [item.__class__(item.chunk, item.score, item.lexical_score, item.semantic_score, item.coverage, item.bm25_score, item.authority_score, item.freshness_score, item.provenance_score, item.support_score, 0.35, item.accepted, item.rejection_reason) for item in accepted]
    return EvidenceDecision(tuple(accepted), tuple(rejected), tuple(conflicts))
