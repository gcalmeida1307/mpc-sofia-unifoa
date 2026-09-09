"""Evidence policy for the high-risk Medicina module."""

from __future__ import annotations

from pathlib import Path

from ..query_analysis import normalize
from .base import (
    DomainRetrievalPackage,
    QueryProfile,
    SourceSelection,
    named_source_paths,
)


def _classification(path: Path) -> bool:
    name = normalize(path.name)
    return any(marker in name for marker in ("cid-", "cid_", "icd-", "icd_", "cif", "classific"))


def _clinical(path: Path) -> bool:
    name = normalize(path.name)
    return any(marker in name for marker in ("clinical", "guideline", "guidance", "sleep", "sono", "protocol", "protocolo", "consensus", "consenso", "nih", "nhlbi", "cdc"))


class MedicalPackage(DomainRetrievalPackage):
    id = "medical"

    def expand_query(self, query: str) -> str:
        normalized = normalize(query)
        additions: list[str] = []
        if any(term in normalized for term in ("sono", "dormir", "sonolencia", "piscada", "microssono")):
            additions.append("sonolencia diurna microssono privacao de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano medicamentos sedativos")
        if "gripe" in normalized or "influenza" in normalized:
            additions.append("influenza infeccao respiratoria virus sintomas febre tosse")
        return f"{query} {' '.join(additions)}".strip()

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        sleep = any(term in normalized for term in ("sono", "dormir", "sonolencia", "piscada", "microssono"))
        base = super().profile(query)
        definition = any(m in normalized for m in ("defina", "definicao", "o que e", "explique", "conceito")) and not any(m in normalized for m in ("codigo", "cid", "icd"))
        return QueryProfile(
            summary=base.summary,
            features=base.features | frozenset({"clinical_sleep"} if sleep else ()) | frozenset({"clinical_definition"} if definition else ()),
            seed_markers=("microssono", "sonolencia diurna", "privacao de sono", "sono insuficiente", "apneia obstrutiva do sono") if sleep else (),
            comparison=base.comparison,
        )

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        profile = self.profile(query)
        selected = named_source_paths(paths, query)
        if selected:
            return SourceSelection(selected, profile, tuple(selected))
        if "clinical_sleep" in profile.features:
            clinical = tuple(path for path in paths if _clinical(path) and not _classification(path))
            if clinical:
                return SourceSelection(clinical, profile)
        return SourceSelection(tuple(paths), profile)

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        if "clinical_definition" in profile.features and _classification(path):
            return False
        if "clinical_sleep" not in profile.features:
            return True
        return not _classification(path) and (_clinical(path) or any(marker in text for marker in profile.seed_markers))

    def score_bonus(self, path: Path, text: str, query_terms: set[str], profile: QueryProfile) -> float:
        del query_terms
        if "clinical_sleep" in profile.features and any(marker in text for marker in profile.seed_markers):
            return 0.62
        if any(term in text for term in ("gripe", "influenza")):
            return 0.24
        del path
        return 0.0

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["clinical-source-gate", "classification-separation"], "isolated": True, "high_risk": True}
