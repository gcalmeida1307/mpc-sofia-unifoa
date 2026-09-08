"""Retrieval policy for the Departamento Pessoal domain."""

from __future__ import annotations

from pathlib import Path

from ..query_analysis import normalize
from .base import QueryProfile
from .legal import LegalPackage


class PersonnelPackage(LegalPackage):
    """Reuse labour-law vocabulary but guard the department-definition query."""

    id = "personnel"

    def profile(self, query: str) -> QueryProfile:
        profile = super().profile(query)
        if "departamento pessoal" not in normalize(query):
            return profile
        return QueryProfile(
            summary=profile.summary,
            features=profile.features | frozenset({"department_definition"}),
            seed_markers=profile.seed_markers,
            required_markers=profile.required_markers,
            summary_markers=profile.summary_markers,
            comparison=profile.comparison,
        )

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        if "department_definition" in profile.features:
            return "departamento pessoal" in text and sum(
                marker in text
                for marker in (
                    "folha de pagamento",
                    "admissao",
                    "ferias",
                    "rescisao",
                    "registro de empregados",
                    "rotinas trabalhistas",
                )
            ) >= 3
        return super().filter_text(path, text, profile)

    def manifest(self) -> dict[str, object]:
        return {
            "id": self.id,
            "features": ["labour-law-vocabulary", "role-definition-gate"],
            "isolated": True,
        }
