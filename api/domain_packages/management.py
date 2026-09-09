"""Retrieval policy for operational management and production variance queries.

Management corpora commonly contain the word ``production`` in unrelated
contexts (for example, production of documents or production of a report).
This package makes a production-deviation question evidence-driven: a passage
must describe a production context and at least one measurable control such as
target, planned, actual, variance, loss or productivity.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..query_analysis import normalize
from .base import DomainRetrievalPackage, QueryProfile


_PRODUCTION_CONTEXT = (
    "producao",
    "produzido",
    "produzida",
    "produzidas",
    "ordem de producao",
    "linha de producao",
    "processo produtivo",
    "unidade produzida",
    "volume produzido",
    "capacidade produtiva",
)

_PRODUCTION_MEASURES = (
    "meta",
    "metas",
    "planejado",
    "planejada",
    "planejamento",
    "realizado",
    "realizada",
    "realizadas",
    "desvio",
    "desvios",
    "variacao",
    "variacoes",
    "perda",
    "perdas",
    "indicador",
    "indicadores",
    "produtividade",
    "eficiencia",
    "rendimento",
    "quantidade produzida",
)

_VARIANCE_COMPARATORS = (
    "meta",
    "metas",
    "planejado",
    "planejada",
    "planejamento",
    "realizado",
    "realizada",
    "realizadas",
    "variacao",
    "variacoes",
    "perda",
    "perdas",
    "indicador",
    "indicadores",
    "produtividade",
    "eficiencia",
    "rendimento",
)


def _production_variance_query(query: str) -> bool:
    normalized = normalize(query)
    has_context = any(marker in normalized for marker in _PRODUCTION_CONTEXT)
    has_measure = any(marker in normalized for marker in _PRODUCTION_MEASURES)
    return (
        ("desvio" in normalized or "variacao" in normalized)
        and has_context
    ) or (
        has_context
        and has_measure
        and any(marker in normalized for marker in ("ver", "acompanhar", "medir", "controle", "analise", "analise", "calcular", "identificar", "como"))
    )


class ManagementPackage(DomainRetrievalPackage):
    """Keep production analysis separate from generic governance material."""

    id = "management"

    def expand_query(self, query: str) -> str:
        profile = self.profile(query)
        if "production_variance" not in profile.features:
            return query
        return (
            f"{query} produção meta planejado realizado desvio variação perdas "
            "indicador produtividade eficiência volume produzido ordem de produção"
        ).strip()

    def profile(self, query: str) -> QueryProfile:
        base = super().profile(query)
        features = set(base.features)
        if _production_variance_query(query):
            features.add("production_variance")
        return QueryProfile(
            summary=base.summary,
            features=frozenset(features),
            seed_markers=("desvio", "variacao", "meta", "realizado") if "production_variance" in features else (),
            required_markers=_PRODUCTION_MEASURES if "production_variance" in features else (),
            summary_markers=base.summary_markers,
            comparison=base.comparison,
        )

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        del path
        if "production_variance" not in profile.features:
            return True
        normalized = normalize(text)
        # Evaluate the relationship in a local sentence/window. Looking at a
        # whole scraped page is not enough: a governance page can mention
        # “produção”, “meta” and “indicadores” in unrelated sections while
        # never documenting a production variance.
        units = [
            unit.strip()
            for unit in re.split(r"(?:[.!?;]\s+|\n+)", normalized)
            if unit.strip()
        ]
        for unit in units:
            has_context = any(marker in unit for marker in _PRODUCTION_CONTEXT)
            has_deviation = any(marker in unit for marker in ("desvio", "desvios", "variacao", "variacoes"))
            comparator_count = sum(marker in unit for marker in _VARIANCE_COMPARATORS)
            if has_context and has_deviation and comparator_count >= 1:
                return True
        # Some extracted tables lose punctuation and arrive as one long line.
        # Keep the same semantic contract using a bounded character window,
        # never the entire document.
        for deviation in ("desvio", "desvios", "variacao", "variacoes"):
            start = 0
            while True:
                position = normalized.find(deviation, start)
                if position < 0:
                    break
                window = normalized[max(0, position - 180):position + 180]
                if (
                    any(marker in window for marker in _PRODUCTION_CONTEXT)
                    and any(marker in window for marker in _VARIANCE_COMPARATORS)
                ):
                    return True
                start = position + len(deviation)
        return False

    def score_bonus(self, path: Path, text: str, query_terms: set[str], profile: QueryProfile) -> float:
        del path, query_terms
        if "production_variance" not in profile.features:
            return 0.0
        normalized = normalize(text)
        measure_count = sum(marker in normalized for marker in _PRODUCTION_MEASURES)
        return min(0.36, 0.08 * measure_count)

    def manifest(self) -> dict[str, object]:
        return {
            "id": self.id,
            "features": ["production-variance-evidence-gate", "metric-aware"],
            "isolated": True,
        }
