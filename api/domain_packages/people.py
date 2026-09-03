"""Retrieval policies for HR and Personnel Department."""

from __future__ import annotations

from pathlib import Path

from ..query_analysis import normalize
from .base import DomainRetrievalPackage, QueryProfile


class PeoplePackage(DomainRetrievalPackage):
    id = "people"

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        features: set[str] = set()
        if any(term in normalized for term in ("contrat", "admiss", "recrut", "selec")):
            features.add("hiring")
        if "departamento pessoal" in normalized:
            features.add("department_definition")
        return QueryProfile(summary=super().profile(query).summary, features=frozenset(features))

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        del path
        if "hiring" in profile.features:
            return any(marker in text for marker in ("recrutamento", "admissao", "documentos admissionais", "vinculo empregaticio", "contratacao de pessoal", "integracao de novos", "selecao de pessoas", "entrevista de selecao"))
        if "department_definition" in profile.features:
            return "departamento pessoal" in text or (sum(marker in text for marker in ("rotinas trabalhistas", "folha de pagamento", "admissao", "ferias", "rescisao", "registro de empregados")) >= 3 and any(marker in text for marker in ("responsavel", "atribuicoes", "compete", "rotinas", "setor", "area")))
        return True

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["hiring-evidence-gate", "role-definition-gate"], "isolated": True}
