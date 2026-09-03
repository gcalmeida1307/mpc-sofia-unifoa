"""Retrieval policy for Direito and Departamento Pessoal."""

from __future__ import annotations

from pathlib import Path

from ..query_analysis import normalize
from .base import (
    DomainRetrievalPackage,
    QueryProfile,
    SourceSelection,
    named_source_paths,
)


def _agreement_paths(paths: list[Path]) -> tuple[Path, ...]:
    return tuple(path for path in paths if any(marker in normalize(path.stem) for marker in ("saae", "acordo", "convenc", "coletiv", "sindicato")))


class LegalPackage(DomainRetrievalPackage):
    id = "legal"

    def expand_query(self, query: str) -> str:
        normalized = normalize(query)
        additions: list[str] = []
        vocabulary = {
            "lei": "legislacao norma artigo dispositivo jurisprudencia aplicacao",
            "direit": "direitos remuneracao salario jornada ferias beneficios adicionais licencas clausulas",
            "acordo coletivo": "convencao coletiva clausula sindicato categoria beneficio remuneracao jornada",
            "hora": "horas extra extras extraordinarias jornada art. 59 duracao diaria limite duas",
            "funcion": "empregado trabalhador empregador contrato trabalho",
            "falt": "falta faltas ausencia ausente jornada desconto remuneracao",
            "negativ": "horas negativas saldo devedor compensacao banco de horas acordo",
            "adiantamento": "decimo terceiro salario gratificacao natalina antecipacao pagamento",
            "decimo terceiro": "decimo terceiro salario gratificacao natalina adiantamento antecipacao",
            "13": "decimo terceiro salario gratificacao natalina adiantamento antecipacao",
        }
        for key, value in vocabulary.items():
            if key in normalized:
                additions.append(value)
        return f"{query} {' '.join(additions)}".strip()

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        summary = super().profile(query).summary
        features: set[str] = set()
        if any(term in normalized for term in ("brecha", "artigo", "jurisprudencia", "sustentar", "argumento")):
            features.add("comparison")
        if any(term in normalized for term in ("problema", "interpretacao", "inconclusiv", "ambigu", "lacuna", "conflito", "contradicao", "divergencia")):
            features.add("review")
        if any(term in normalized for term in ("hora", "horas", "extra", "jornada")):
            features.add("overtime")
        if "dia ponte" in normalized or "dias ponte" in normalized:
            features.add("bridge_day")
        if any(term in normalized for term in ("hora negativa", "horas negativas", "saldo devedor", "negativa")):
            features.add("negative_hours")
        if any(term in normalized for term in ("falta", "faltas", "ausencia", "ausente")):
            features.add("absence")
        if any(term in normalized for term in ("compensacao", "compensar", "repor", "diferenca", "devendo")):
            features.add("compensation")
        if "assedio" in normalized:
            features.add("harassment")
        if any(term in normalized for term in ("punicao", "punir", "pena", "penalidade", "sancao")):
            features.add("sanction")
        markers = {
            "comparison": ("horas extras", "horas suplementares", "jornada de trabalho", "banco de horas", "compensacao", "jurisprudencia", "precedentes", "art. 59."),
            "review": ("clausula 5", "360 dias", "horas extras nao compensadas", "dias pontes", "problemas oriundos da aplicacao", "vigencia da presente convencao"),
        }
        seed = tuple(dict.fromkeys(marker for feature in features for marker in markers.get(feature, ())))
        return QueryProfile(summary=summary, features=frozenset(features), seed_markers=seed)

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        profile = self.profile(query)
        selected = named_source_paths(paths, query)
        normalized = normalize(query)
        links = tuple(path for path in paths if path.parent.name.casefold() == "links")
        if selected:
            if "comparison" in profile.features and links:
                selected = tuple(dict.fromkeys([*selected, *links]))
            if retry:
                selected = tuple(dict.fromkeys([*selected, *(path for path in paths if path.parent.name.casefold() in {"links", "research", "offline"})]))
            return SourceSelection(selected, profile)
        if "agreement" in normalized or "acordo coletivo" in normalized or "convencao coletiva" in normalized or "dia ponte" in normalized:
            agreements = _agreement_paths(paths)
            if agreements:
                return SourceSelection(agreements, profile)
        if "jurisprudencia" in profile.features and links:
            return SourceSelection(links, profile)
        return SourceSelection(tuple(paths), profile)

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        del path
        if "absence" in profile.features and not any(marker in text for marker in ("falta injustificada", "faltas injustificadas", "ausencia injustificada", "desconto salarial", "perda do salario", "repouso semanal remunerado")):
            return False
        if "compensation" in profile.features and not any(marker in text for marker in ("compens", "banco de horas", "saldo", "repor", "diferenca")):
            return False
        if "negative_hours" in profile.features and not any(marker in text for marker in ("negativ", "saldo devedor", "compensacao", "diminuicao correspondente", "horas extras nao compensadas", "horas suplementares nao compensadas")):
            return False
        if "harassment" in profile.features and any(term in profile.features for term in ("sanction",)):
            return any(marker in text for marker in ("pun", "sanc", "pena", "penalidade", "advertencia", "demissao", "justa causa", "multa"))
        return True

    def seed_candidates(self, text: str, profile: QueryProfile) -> bool:
        return any(marker in text for marker in profile.seed_markers)

    def score_bonus(self, path: Path, text: str, query_terms: set[str], profile: QueryProfile) -> float:
        bonus = 0.0
        if "overtime" in profile.features and ("art. 59." in text or "duracao diaria do trabalho podera ser acrescida" in text):
            bonus += 0.42
        if "negative_hours" in profile.features and "compens" in text:
            bonus += 0.20
        if "bridge_day" in profile.features and any(marker in text for marker in ("dias pontes", "dia ponte")):
            bonus += 0.34
        if "comparison" in profile.features and path.parent.name.casefold() == "links":
            bonus += 0.08
        del query_terms
        return bonus

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["comparison", "review", "provenance-aware-source-selection"], "isolated": True}
