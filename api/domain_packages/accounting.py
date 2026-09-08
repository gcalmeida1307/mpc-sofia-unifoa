"""Retrieval policy for accounting statements and reporting."""

from __future__ import annotations

from pathlib import Path

from ..query_analysis import normalize
from .base import DomainRetrievalPackage, QueryProfile


class AccountingPackage(DomainRetrievalPackage):
    id = "accounting"

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        balance = any(term in normalized for term in ("balan", "patrimonial", "demonstracao"))
        base = super().profile(query)
        features = set(base.features)
        if balance:
            features.add("balance")
        return QueryProfile(
            summary=base.summary,
            features=frozenset(features),
            required_markers=("balanco patrimonial", "ativo circulante", "passivo circulante", "patrimonio liquido", "demonstracoes contabeis", "notas explicativas") if balance else (),
            comparison=base.comparison,
        )

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        del path
        if "balance" not in profile.features:
            return True
        return sum(marker in text for marker in profile.required_markers) >= 2

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["balance-evidence-gate"], "isolated": True}
