"""Retrieval policy for Direito and Departamento Pessoal."""

from __future__ import annotations

import re
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
            "abuso de poder": "abuso de poder assedio moral denuncia cipa ouvidoria corregedoria sigilo confidencialidade anonimato retaliacao perseguicao protecao trabalhador",
            "denuncia": "denuncia assedio moral cipa abuso de poder canal de denuncia ouvidoria corregedoria sigilo confidencialidade anonimato retaliacao protecao trabalhador",
            "persegu": "retaliacao perseguicao represalia denuncia assedio moral abuso de poder protecao trabalhador sigilo confidencialidade canal de denuncia",
            # Keep sexual-criminal anchors context-aware.  A generic
            # "assédio moral" question must not be expanded into art. 216-A
            # or 215-A, otherwise the lexical retriever can pull sexual-law
            # pages into a workplace-bullying answer.
            "importun": "importunacao sexual art. 215-A 215-A ato libidinoso pratica libidinosa sem consentimento assedio sexual ambiente de trabalho trabalhador empregador",
            # An "atraso" question needs attendance/timekeeping provisions,
            # not an arbitrary occurrence of the word in a legal code.
            "atras": "atrasado atraso pontualidade registro de ponto variacoes horario cinco minutos dez minutos tempo transporte compensado repouso remunerado clausula 27 art. 58",
            "transit": "tempo transporte deslocamento registro de ponto horario atraso justificativa",
        }
        for key, value in vocabulary.items():
            if key in normalized:
                additions.append(value)
        if "assedio sexual" in normalized or ("assedio" in normalized and "importunacao" in normalized):
            additions.append("assedio sexual art. 216-A 216-A constranger superior hierarquico favorecimento sexual relacao de emprego")
        elif "assedio moral" in normalized:
            additions.append("assedio moral ambiente de trabalho violencia psicologica conduta repetitiva trabalhador empregador")
        elif "assedio" in normalized:
            # Plain "assédio" is ambiguous. Retrieve both candidate senses,
            # then let the domain filter and Evidence Judge decide; do not
            # silently assume that it is sexual or moral harassment.
            additions.append("assedio moral assedio sexual art. 216-A constranger ambiente de trabalho")
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
        if (
            not features
            and any(term in normalized for term in ("direito trabalhista", "direito do trabalho", "vinculo", "carteira assinada", "emprego", "empregado"))
        ):
            # Broad legal questions still need a primary normative source. A
            # web capture about labour law is commentary, not the legal basis
            # of the answer.
            features.add("general_legal")
        if any(
            marker in normalized
            for marker in ("dois vinculos", "dois empregos", "dois contratos", "carteira assinada")
        ):
            features.add("multiple_employment")
        if any(term in normalized for term in ("brecha", "artigo", "jurisprudencia", "sustentar", "argumento")):
            features.add("comparison")
        if "saae" in normalized and any(
            term in normalized for term in ("vade", "vademecum", "mecum", "mencum")
        ):
            # Mentioning both instruments is a two-source request even when
            # the user phrases it as two questions instead of saying
            # ``compare`` explicitly.
            features.add("comparison")
        if any(term in normalized for term in ("problema", "interpretacao", "inconclusiv", "ambigu", "lacuna", "conflito", "contradicao", "divergencia")):
            features.add("review")
        if any(term in normalized for term in ("hora", "horas", "extra", "jornada")):
            features.add("overtime")
        if any(term in normalized for term in ("atras", "pontual", "minuto", "transito", "transporte")):
            features.add("lateness")
        if "dia ponte" in normalized or "dias ponte" in normalized:
            features.add("bridge_day")
        if any(term in normalized for term in ("hora negativa", "horas negativas", "saldo devedor", "negativa")):
            features.add("negative_hours")
        if any(term in normalized for term in ("falta", "faltas", "ausencia", "ausente")):
            features.add("absence")
        if any(term in normalized for term in ("compensacao", "compensar", "repor", "devendo")) or (
            "diferenca" in normalized
            and any(term in normalized for term in ("hora", "jornada", "saldo", "compens"))
        ):
            features.add("compensation")
        if any(term in normalized for term in ("assedio", "importunacao", "abuso de poder", "denuncia", "denunciar", "perseguicao", "retaliacao", "represalia", "sem me expor", "anonimo", "anonimato")):
            features.add("harassment")
        if "assedio moral" in normalized:
            features.add("moral_harassment")
        if "assedio sexual" in normalized:
            features.add("sexual_harassment")
        if any(term in normalized for term in ("punicao", "punir", "pena", "penalidade", "sancao")):
            features.add("sanction")
        if "mandado de seguranca" in normalized and any(
            term in normalized
            for term in ("prazo", "impetrar", "ajuizar", "decadencia", "quando")
        ):
            features.add("writ_deadline")
        if re.search(r"\b\d{1,2}:\d{2}\b", normalized) and len(re.findall(r"\b\d{1,2}:\d{2}\b", normalized)) >= 2:
            features.add("journey_calculation")
        if any(term in normalized for term in ("dsr", "descanso semanal", "repouso semanal")):
            features.add("dsr")
        markers = {
            "comparison": ("horas extras", "horas suplementares", "jornada de trabalho", "banco de horas", "compensacao", "jurisprudencia", "precedentes", "art. 59."),
            "review": ("clausula 5", "360 dias", "horas extras nao compensadas", "dias pontes", "problemas oriundos da aplicacao", "vigencia da presente convencao"),
            "lateness": ("clausula 27", "chegar atrasado", "atrasado", "registro de ponto", "cinco minutos", "dez minutos", "tempo despendido", "repouso remunerado"),
            "journey_calculation": ("jornada", "registro de ponto", "horas extras", "art. 58", "art. 59", "duracao diaria"),
            "dsr": ("dsr", "repouso semanal remunerado", "descanso semanal remunerado", "repouso semanal"),
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
        if "general_legal" in features and len(features) > 1:
            # A specialized contract (deadline, overtime, lateness, etc.) has
            # its own source and passage gate; do not let the broad labour
            # filter hide the specialized statute that also mentions work.
            features.discard("general_legal")
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
        if "general_legal" in profile.features and "multiple_employment" not in profile.features:
            primary = tuple(
                path
                for path in paths
                if path.suffix.casefold() in {".pdf", ".docx"}
                and any(marker in normalize(path.stem) for marker in ("vade", "clt", "lei trabalhista"))
            )
            if primary:
                return SourceSelection(primary, profile)
        if "agreement" in normalized or "acordo coletivo" in normalized or "convencao coletiva" in normalized or "dia ponte" in normalized:
            agreements = _agreement_paths(paths)
            if agreements:
                return SourceSelection(agreements, profile)
        if "jurisprudencia" in profile.features and links:
            return SourceSelection(links, profile)
        if "overtime" in profile.features:
            # A generic overtime question should start with the normative
            # source, not with a blog that happens to repeat words such as
            # ``trabalho`` or ``horas``.  Named agreements already returned
            # above keep their explicit-source contract.
            primary = tuple(
                path
                for path in paths
                if any(marker in normalize(path.stem) for marker in ("vade", "clt", "lei trabalhista"))
            )
            if primary:
                return SourceSelection(primary, profile)
        return SourceSelection(tuple(paths), profile)

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        # Keep front matter and unrelated statutes out of a generic labour
        # explanation. The source is allowed only when the passage itself
        # contains an employment-law anchor.
        if "general_legal" in profile.features and "multiple_employment" not in profile.features and not any(
            marker in text
            for marker in (
                "contrato de trabalho",
                "relação de emprego",
                "relacao de emprego",
                "empregado",
                "empregador",
                "carteira de trabalho",
                "jornada de trabalho",
                "salário",
                "salario",
                "direito do trabalho",
            )
        ):
            return False
        if "multiple_employment" in profile.features and not any(
            marker in text
            for marker in ("dois vinculos", "dois empregos", "dois contratos", "carteira de trabalho", "vinculo empregaticio")
        ):
            return False
        if "harassment" in profile.features and not any(
            marker in text
            for marker in (
                "assedio moral",
                "assedio sexual",
                "importunacao",
                "importunacao sexual",
                "abuso de poder",
                "denuncia",
                "canal de denuncia",
                "ouvidoria",
                "corregedoria",
                "sigilo",
                "confidencialidade",
                "anonimato",
                "retaliacao",
                "perseguicao",
                "represalia",
                "cipa",
                "rescisao indireta",
                "art. 483",
                "rigor excessivo",
            )
        ):
            # A generic employment-law passage cannot support a question about
            # reporting abuse or staying protected at work. Keep the query in
            # the evidence route, but force the answer to declare a gap when
            # the corpus has no complaint/protection rule.
            return False
        if "harassment" in profile.features:
            direct_markers = (
                "assedio moral",
                "assedio sexual",
                "abuso de poder",
                "canal de denuncia",
                "ouvidoria",
                "corregedoria",
                "sigilo",
                "confidencialidade",
                "anonimato",
                "retaliacao",
                "perseguicao",
                "represalia",
                "cipa",
            )
            workplace_markers = (
                "trabalho",
                "trabalhador",
                "empregado",
                "empregador",
                "empresa",
                "ambiente de trabalho",
                "cipa",
                "relacao de emprego",
                "contrato de trabalho",
            )
            navigation_markers = (
                "receitas",
                "despesas",
                "licitacoes",
                "servidores",
                "concursos",
                "dados abertos",
                "painel",
                "informacoes classificadas",
                "servico de informacoes",
                "acordos de cooperacao",
                "relatorios",
            )
            if not any(marker in text for marker in direct_markers):
                return False
            if "moral_harassment" in profile.features and not (
                ("assedio moral" in text or ("assedio" in text and "assedio sexual" not in text) or "cipa" in text)
                and any(marker in text for marker in workplace_markers)
            ):
                return False
            if "sexual_harassment" in profile.features and not any(
                marker in text
                for marker in (
                    "trabalho", "trabalhador", "empregado", "empregador", "empresa", "relacao de emprego",
                    "emprego", "superior hierarquico", "ascendencia inerente",
                )
            ):
                return False
            if sum(text.count(marker) for marker in navigation_markers) >= 5:
                # A page title such as “Guia de Prevenção ao Assédio” is not
                # the guide itself when the capture is mostly a site menu.
                return False
        overtime_anchor = any(
            marker in text
            for marker in (
                "horas extras",
                "horas suplementares",
                "horas extraordinarias",
                "jornada de trabalho",
                "duracao diaria do trabalho",
                "duracao do trabalho",
            )
        ) or (
            "art. 59" in text
            and any(marker in text for marker in ("acrescimo", "salario-hora"))
        )
        if "overtime" in profile.features and "lateness" not in profile.features and not overtime_anchor:
            # A legal PDF contains many unrelated occurrences of ``trabalho``
            # and ``horas``.  They are not evidence for an overtime question;
            # require the actual working-time rule before the ranker sees it.
            # An agreement clause is the intentional exception: in a named
            # comparison it can express compensation without repeating the
            # statutory phrase ``horas extras``.  It still needs a concrete
            # compensation/jornada marker, so a random page from the same
            # document cannot pass merely because its filename was named.
            agreement_pass = (
                "comparison" in profile.features
                and any(marker in normalize(path.name) for marker in ("saae", "acordo", "convenc", "coletiv"))
                and any(marker in text for marker in ("compens", "saldo", "jornada", "360 dias"))
            )
            if not agreement_pass:
                return False
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
        if "lateness" in profile.features and not any(
            marker in text
            for marker in profile.seed_markers
            if marker in ("clausula 27", "chegar atrasado", "atrasado", "registro de ponto", "cinco minutos", "dez minutos", "tempo despendido", "repouso remunerado")
        ):
            return False
        if "lateness" in profile.features and not (
            "clausula 27" in text
            or "chegar atrasado" in text
            or ("art. 58" in text and "registro de ponto" in text)
        ):
            # A page about mining, procurement or another employment topic
            # may contain "tempo", "transporte" or "registro de ponto" but
            # still cannot support the requested attendance rule.
            return False
        if "journey_calculation" in profile.features:
            rule_anchor = any(marker in text for marker in ("registro de ponto", "horas extras", "horas suplementares", "art. 58", "art. 59"))
            journey_anchor = any(marker in text for marker in ("jornada", "limite maximo", "duracao diaria", "registro de ponto"))
            # A combined delay question has two valid documentary sides:
            # SAAE may define how an authorized late arrival is compensated,
            # while the Vade/CLT defines the general working-time rule. The
            # agreement clause does not need to repeat ``horas extras`` to be
            # relevant to that question.
            lateness_anchor = "lateness" in profile.features and any(
                marker in text for marker in ("clausula 27", "chegar atrasado", "atraso for compensado")
            )
            if not lateness_anchor and not (rule_anchor and journey_anchor):
                return False
        if "dsr" in profile.features and "journey_calculation" not in profile.features and not any(
            marker in text for marker in ("dsr", "repouso semanal remunerado", "descanso semanal remunerado")
        ):
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
        if "lateness" in profile.features:
            if "clausula 27" in text or "chegar atrasado" in text:
                bonus += 0.48
            if "registro de ponto" in text or "cinco minutos" in text or "tempo despendido" in text:
                bonus += 0.42
        if "bridge_day" in profile.features and any(marker in text for marker in ("dias pontes", "dia ponte")):
            bonus += 0.34
        if "writ_deadline" in profile.features and "mandado de seguranca" in text:
            bonus += 0.35
            if any(marker in text for marker in profile.required_markers[1:]):
                bonus += 0.35
        if "journey_calculation" in profile.features and any(marker in text for marker in ("jornada", "registro de ponto", "horas extras", "art. 58", "art. 59")):
            bonus += 0.34
        if "dsr" in profile.features and any(marker in text for marker in ("dsr", "repouso semanal", "descanso semanal")):
            bonus += 0.38
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
        if "harassment" in profile.features:
            # Exact statutory anchors must outrank generic legal pages that
            # merely contain words such as "diferença" or "conduta".
            if "art. 215-a" in text or "importunacao sexual" in text:
                bonus += 0.86
            if "art. 216-a" in text or "assedio sexual" in text:
                bonus += 0.86
            if "assedio moral" in text:
                bonus += 0.58
            if "constranger" in text or "ato libidinoso" in text:
                bonus += 0.22
        if "review" in profile.features:
            if "clausula 5" in text or "cláusula 5" in text:
                bonus += 0.46
            if "problemas oriundos da aplicacao" in text or "problemas oriundos da aplicação" in text:
                bonus += 0.24
            if "clausula 25" in text or "cláusula 25" in text:
                bonus += 0.18
        del query_terms
        return bonus

    def finalize(self, candidates: list, profile: QueryProfile) -> list:
        """Keep a time calculation focused on the actual labor rule."""

        if "harassment" in profile.features:
            anchored = [
                item
                for item in candidates
                if any(
                    marker in normalize(item.chunk.text)
                    for marker in ("art. 215-a", "art. 216-a", "importunacao sexual", "assedio sexual", "assedio moral", "cipa")
                )
            ]
            if anchored:
                anchored_keys = {id(item) for item in anchored}
                remainder = [item for item in candidates if id(item) not in anchored_keys]
                return [*sorted(anchored, key=lambda item: item.score, reverse=True), *remainder]

        if "journey_calculation" not in profile.features:
            return candidates
        if "lateness" in profile.features:
            # Preserve both halves of a delayed-arrival question. The SAAE
            # clause and the general jornada rule are complementary, not
            # competing hits; discarding either side creates a false
            # ``missing evidence`` result in a named-source follow-up.
            focused = [
                item
                for item in candidates
                if any(
                    marker in normalize(item.chunk.text)
                    for marker in (
                        "clausula 27",
                        "chegar atrasado",
                        "atraso for compensado",
                        "registro de ponto",
                        "horas extras",
                        "horas suplementares",
                        "art. 58",
                        "art. 59",
                    )
                )
            ]
            if focused:
                return focused
        preferred = [
            item for item in candidates
            if any(marker in normalize(item.chunk.path.name) for marker in ("vade", "clt", "trabalh"))
        ]
        pool = preferred or candidates
        focused = [
            item for item in pool
            if any(marker in normalize(item.chunk.text) for marker in ("horas extras", "horas suplementares", "registro de ponto", "art. 58", "art. 59"))
            and any(marker in normalize(item.chunk.text) for marker in ("jornada", "limite maximo", "duracao diaria", "registro de ponto"))
        ]
        # Two passages are enough for the calculation (rule + limitation).
        # A full legal code page is not a license to attach neighboring laws.
        return (focused or pool)[:2]

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["comparison", "review", "provenance-aware-source-selection"], "isolated": True}
