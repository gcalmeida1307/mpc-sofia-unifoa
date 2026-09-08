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
            "mandado de seguranca": "lei 12.016 artigo 23 prazo decadencial cento e vinte dias ato coator ciencia do interessado",
        }
        for key, value in vocabulary.items():
            if key in normalized:
                additions.append(value)
        if any(term in normalized for term in ("ambigu", "interpret", "erro", "problema", "inconclus", "lacuna")):
            additions.append("clausula redação interpretação lacuna conflito aplicação vigência registro autorização")
        if any(term in normalized for term in ("compar", "confront", "versus", "diferenca entre")):
            additions.append("clausula 5 compensação jornada horas extras adicional 50% art. 59 CLT")
        return f"{query} {' '.join(additions)}".strip()

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        base = super().profile(query)
        summary = base.summary
        features: set[str] = set(base.features)
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
        if "mandado de seguranca" in normalized and any(
            term in normalized
            for term in ("prazo", "impetrar", "ajuizar", "decadencia", "quando")
        ):
            features.add("writ_deadline")
        markers = {
            "comparison": ("horas extras", "horas suplementares", "jornada de trabalho", "banco de horas", "compensacao", "jurisprudencia", "precedentes", "art. 59."),
            "review": ("clausula 5", "360 dias", "horas extras nao compensadas", "dias pontes", "problemas oriundos da aplicacao", "vigencia da presente convencao"),
        }
        seed = tuple(dict.fromkeys(marker for feature in features for marker in markers.get(feature, ())))
        required_markers = (
            "mandado de seguranca",
            "cento e vinte dias",
            "120 dias",
            "prazo decadencial",
            "art. 23",
            "lei 12.016",
        ) if "writ_deadline" in features else ()
        return QueryProfile(
            summary=summary,
            features=frozenset(features),
            seed_markers=seed,
            required_markers=required_markers,
            comparison="comparison" in features,
        )

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        profile = self.profile(query)
        selected = named_source_paths(paths, query)
        normalized = normalize(query)
        links = tuple(path for path in paths if path.parent.name.casefold() == "links")
        if selected:
            required = tuple(selected)
            if "comparison" in profile.features and links and any(term in normalized for term in ("link", "jurisprud", "precedent")):
                selected = tuple(dict.fromkeys([*selected, *links]))
            if retry and (not profile.comparison or any(term in normalized for term in ("link", "jurisprud", "precedent"))):
                selected = tuple(dict.fromkeys([*selected, *(path for path in paths if path.parent.name.casefold() in {"links", "research", "offline"})]))
            return SourceSelection(selected, profile, required)
        if "agreement" in normalized or "acordo coletivo" in normalized or "convencao coletiva" in normalized or "dia ponte" in normalized:
            agreements = _agreement_paths(paths)
            if agreements:
                return SourceSelection(agreements, profile)
        if "jurisprudencia" in profile.features and links:
            return SourceSelection(links, profile)
        return SourceSelection(tuple(paths), profile)

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        del path
        if "writ_deadline" in profile.features:
            # A constitutional definition or a generic occurrence of the word
            # “prazo” is not enough. The passage must contain the writ and the
            # deadline rule together; otherwise the orchestrator must treat
            # the local corpus as incomplete and use its authorized fallback.
            return "mandado de seguranca" in text and any(
                marker in text for marker in profile.required_markers[1:]
            )
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
        if "writ_deadline" in profile.features and "mandado de seguranca" in text:
            bonus += 0.35
            if any(marker in text for marker in profile.required_markers[1:]):
                bonus += 0.35
        if "comparison" in profile.features and path.parent.name.casefold() == "links":
            bonus += 0.12
            if any(marker in path.name.casefold() for marker in ("stj", "stf", "gov-br", "planalto")):
                bonus += 0.20
        if "comparison" in profile.features:
            source_name = path.name.casefold()
            if any(marker in source_name for marker in ("saae", "acordo", "convenc", "coletiv")):
                bonus += 0.34
            if "vade" in source_name or "clt" in source_name:
                bonus += 0.16
        if "comparison" in profile.features and "art. 59." in text:
            bonus += 0.28
        if "review" in profile.features:
            if "clausula 5" in text or "cláusula 5" in text:
                bonus += 0.46
            if "problemas oriundos da aplicacao" in text or "problemas oriundos da aplicação" in text:
                bonus += 0.24
            if "clausula 25" in text or "cláusula 25" in text:
                bonus += 0.18
        del query_terms
        return bonus

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["comparison", "review", "provenance-aware-source-selection"], "isolated": True}
