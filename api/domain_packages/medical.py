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


SYMPTOM_MARKERS = (
    "tosse", "tossir", "febre", "muco", "catarro", "secrecao", "secreção", "dor",
    "garganta", "coriza", "chiado", "falta de ar", "dispneia", "respiratoria",
    "respiratório", "respiratorio", "gripe", "influenza", "bronquite",
)


def _contains_marker(normalized: str, marker: str) -> bool:
    """Match words, not substrings (``dor`` must not match ``dormir``)."""

    if " " in marker:
        return marker in normalized
    return marker in set(normalized.split())


def is_medical_symptom_query(query: str) -> bool:
    normalized = normalize(query)
    return any(_contains_marker(normalized, marker) for marker in SYMPTOM_MARKERS)


class MedicalPackage(DomainRetrievalPackage):
    id = "medical"

    def expand_query(self, query: str) -> str:
        normalized = normalize(query)
        additions: list[str] = []
        if any(term in normalized for term in ("sono", "dormir", "sonolencia", "piscada", "microssono")):
            additions.append("sonolencia diurna microssono privacao de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano medicamentos sedativos")
        if "gripe" in normalized or "influenza" in normalized:
            additions.append("influenza infeccao respiratoria virus sintomas febre tosse")
        if is_medical_symptom_query(query):
            additions.append("sintomas avaliacao clinica sinais de alerta vias respiratorias tosse febre muco")
        return f"{query} {' '.join(additions)}".strip()

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        sleep = any(term in normalized for term in ("sono", "dormir", "sonolencia", "piscada", "microssono"))
        base = super().profile(query)
        definition = any(m in normalized for m in ("defina", "definicao", "o que e", "explique", "conceito")) and not any(m in normalized for m in ("codigo", "cid", "icd"))
        symptom = is_medical_symptom_query(query)
        symptom_markers = tuple(marker for marker in SYMPTOM_MARKERS if _contains_marker(normalized, marker))
        return QueryProfile(
            summary=base.summary,
            features=base.features | frozenset({"clinical_sleep"} if sleep else ()) | frozenset({"clinical_definition"} if definition else ()) | frozenset({"clinical_symptom"} if symptom else ()),
            seed_markers=("microssono", "sonolencia diurna", "privacao de sono", "sono insuficiente", "apneia obstrutiva do sono") if sleep else symptom_markers,
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
        if "clinical_symptom" in profile.features:
            # Classification tables are useful for coding, not for answering
            # an open symptom question. Keep the active module boundary, but
            # exclude CID/ICD corpora before ranking so they cannot become a
            # diagnosis by lexical accident.
            clinical = tuple(path for path in paths if not _classification(path))
            return SourceSelection(clinical, profile)
        return SourceSelection(tuple(paths), profile)

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        if "clinical_definition" in profile.features and _classification(path):
            return False
        if "clinical_symptom" in profile.features:
            if _classification(path):
                return False
            # A symptom answer needs a passage that mentions a symptom or a
            # clinical respiratory context. A random page about oncology,
            # coding or anatomy is not sufficient merely because it is a PDF.
            return any(marker in text for marker in profile.seed_markers) or any(
                marker in text for marker in ("sintoma", "sinais e sintomas", "avaliacao clinica", "infeccao respiratoria", "vias respiratorias")
            )
        if "clinical_sleep" not in profile.features:
            return True
        return not _classification(path) and (_clinical(path) or any(marker in text for marker in profile.seed_markers))

    def score_bonus(self, path: Path, text: str, query_terms: set[str], profile: QueryProfile) -> float:
        del query_terms
        if "clinical_sleep" in profile.features and any(marker in text for marker in profile.seed_markers):
            return 0.62
        if "clinical_symptom" in profile.features and any(marker in text for marker in profile.seed_markers):
            return 0.42
        if any(term in text for term in ("gripe", "influenza")):
            return 0.24
        del path
        return 0.0

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["clinical-source-gate", "classification-separation", "symptom-context-gate"], "isolated": True, "high_risk": True}
