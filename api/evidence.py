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
    if any(part.casefold() == "offline" for part in path.parts):
        # Provider-generated material is a candidate for recovery, never an
        # authority equivalent to the original document or official source.
        return 0.42
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


def _hard_query_anchors(question: str) -> tuple[str, ...]:
    """Extract identifiers that must be present in supporting evidence.

    Generic word overlap is useful for exploratory questions, but it is not
    safe for laws, articles, file names or software versions. Those queries
    carry a literal anchor and a candidate without that anchor cannot support
    the answer merely because it shares words such as ``informação`` or
    ``versão``.
    """
    normalized = normalize(question)
    anchors: list[str] = []
    anchors.extend(re.findall(r"\b\d{1,4}(?:\.\d{1,4})+\b", normalized))
    for phrase in (
        "acesso a informacao",
        "mandado de seguranca",
        "defeso eleitoral",
        "zabbix",
        "riskusers",
        "riskyusers",
    ):
        if phrase in normalized:
            anchors.append(phrase)
    return tuple(dict.fromkeys(anchors))


def _topic_anchor_groups(question: str) -> tuple[tuple[str, ...], ...]:
    """Return high-signal concepts a supporting passage must address.

    Filename membership is not topical evidence.  This is intentionally a
    small deterministic gate: it catches the dangerous case where a named
    legal code contributes an unrelated page merely because the document was
    explicitly requested.
    """
    normalized = normalize(question)
    def contains(marker: str) -> bool:
        return marker in normalized if " " in marker else marker in set(re.findall(r"[\w]+", normalized))
    groups: list[tuple[str, ...]] = []
    if any(marker in normalized for marker in ("atras", "pontual", "minut", "transit", "transporte")):
        groups.append((
            "atras", "atrasado", "minut", "pontual", "registro de ponto",
            "horario", "tempo despendido", "deslocamento", "transporte",
            "compensado", "repouso remunerado", "cinco minutos", "dez minutos",
        ))
    if "acesso a informacao" in normalized:
        groups.append(("acesso a informacao", "transparencia", "informacoes publicas", "dados publicos"))
    if re.search(r"\b12\.527\b", normalized):
        # A law-number query must be supported by the law number or its
        # unmistakable subject. Navigation menus and personnel tables from
        # the same module are not evidence for the LAI.
        groups.append(("12.527", "lei de acesso a informacao", "acesso a informacao"))
    if "zabbix" in normalized:
        groups.append(("zabbix", "trigger", "host", "item", "monitoramento"))
    if any(marker in normalized for marker in ("riskusers", "riskyusers", "nivel de risco", "estado do risco")):
        groups.append(("riskusers", "riskyusers", "nivel de risco", "estado do risco", "em risco"))
    if "mandado de seguranca" not in normalized and any(
        marker in normalized
        for marker in (
            "direito trabalhista",
            "direito do trabalho",
            "vinculo de carteira",
            "carteira assinada",
            "emprego a",
            "emprego b",
        )
    ):
        groups.append(
            (
                "contrato de trabalho",
                "relacao de emprego",
                "empregado",
                "empregador",
                "carteira de trabalho",
                "jornada de trabalho",
                "salario",
                "direito do trabalho",
            )
        )
    if any(
        marker in normalized
        for marker in (
            "assedio",
            "importunacao",
            "abuso de poder",
            "denuncia",
            "denunciar",
            "perseguicao",
            "retaliacao",
            "represalia",
            "sem me expor",
            "anonimo",
            "anonimato",
        )
    ):
        groups.append(
            (
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
        )
    if len(re.findall(r"\b\d{1,2}:\d{2}\b", normalized)) >= 2 or any(marker in normalized for marker in ("dsr", "descanso semanal", "repouso semanal")):
        groups.append((
            "jornada", "registro de ponto", "horas extras", "hora extra", "art. 58",
            "art. 59", "repouso semanal", "descanso semanal", "dsr",
        ))
    if any(contains(marker) for marker in ("tosse", "febre", "muco", "catarro", "secrecao", "garganta", "coriza", "chiado", "falta de ar", "dispneia", "gripe", "influenza", "bronquite")):
        groups.append((
            "tosse", "febre", "muco", "catarro", "secrecao", "sintoma",
            "sinais e sintomas", "infeccao respiratoria", "vias respiratorias",
            "influenza", "gripe", "bronquite", "respiratorio", "respiratoria",
        ))
    return tuple(groups)


def judge_candidates(question: str, module_id: str, policy: ModulePolicy, candidates: Iterable[Evidence], required_sources: tuple[str, ...] = ()) -> EvidenceDecision:
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
    hard_anchors = _hard_query_anchors(question)
    topic_groups = _topic_anchor_groups(question)
    normalized_question = normalize(question)
    version_anchors = tuple(dict.fromkeys(re.findall(r"\b\d+\.\d+\b", normalized_question)))
    version_comparison = len(version_anchors) >= 2 and any(marker in normalized_question for marker in ("versao", "versoes", "diferenca entre", "compar"))
    accepted: list[Evidence] = []
    rejected: list[Evidence] = []
    conflicts: list[dict[str, Any]] = []
    # A candidate must have both a reasonable composite score and a semantic
    # anchor in the actual question. The previous multiplier made a 0.30
    # module policy effectively accept evidence around 0.21, which allowed
    # broad domain vocabulary to outrank genuinely relevant passages.
    threshold = max(0.28, min(0.68, float(policy.min_evidence_score) * 0.95))
    from .document_pages import text_quality
    from .domain_packages.base import comparison_requested
    compare_named = comparison_requested(question) and len(required_sources) >= 2
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
        anchor_supported = not hard_anchors or any(
            anchor in text or anchor in normalize(candidate.chunk.path.name)
            for anchor in hard_anchors
        )
        topic_supported = all(any(marker in text for marker in group) for group in topic_groups)
        harassment_query = any(
            marker in normalized_question
            for marker in (
                "assedio",
                "importunacao",
                "abuso de poder",
                "denuncia",
                "denunciar",
                "perseguicao",
                "retaliacao",
                "represalia",
                "sem me expor",
                "anonimo",
                "anonimato",
            )
        )
        if harassment_query:
            direct_harassment_markers = (
                "assedio moral",
                "assedio sexual",
                "importunacao",
                "importunacao sexual",
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
            topic_supported = topic_supported and any(marker in text for marker in direct_harassment_markers)
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
            if "assedio moral" in normalized_question:
                topic_supported = topic_supported and (
                    ("assedio moral" in text or ("assedio" in text and "assedio sexual" not in text) or "cipa" in text)
                    and any(marker in text for marker in workplace_markers)
                )
            if "assedio sexual" in normalized_question:
                topic_supported = topic_supported and any(
                    marker in text
                    for marker in (
                        "trabalho",
                        "trabalhador",
                        "empregado",
                        "empregador",
                        "empresa",
                        "relacao de emprego",
                    )
                )
            if sum(text.count(marker) for marker in navigation_markers) >= 5:
                topic_supported = False
        if version_comparison:
            # A versioned filename alone is not enough: a random page from a
            # 7.4 manual must not support a comparison with 8.0. The passage
            # must mention one of the requested versions and discuss a
            # version/change/compatibility concept in the text itself.
            compare_markers = ("alter", "mudan", "novidad", "upgrade", "compatib", "diferenc", "o que ha de novo")
            version_context = any(
                any(marker in text[max(0, index - 220): index + 220] for marker in compare_markers)
                for version in version_anchors
                for index in [text.find(version)]
                if index >= 0
            )
            anchor_supported = anchor_supported and any(version in text for version in version_anchors) and version_context
        has_question_anchor = anchor_supported and topic_supported and (
            question_coverage >= 0.10
            or candidate.coverage >= 0.18
            or candidate.semantic_score >= 0.48
            or (compare_named and candidate.chunk.path.name in required_sources and text_quality(candidate.chunk.text) >= 0.75)
        )
        if judge_score >= threshold and has_question_anchor:
            accepted.append(enriched)
        else:
            reason = "não atingiu relevância, suporte ou proveniência mínimos"
            if hard_anchors and not anchor_supported:
                reason = "não contém no trecho o identificador e o contexto necessários para sustentar a pergunta"
            elif topic_groups and not topic_supported:
                reason = "o trecho pertence à fonte indicada, mas não trata do tema específico da pergunta"
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
                    reason,
                )
            )
    for index, left in enumerate(accepted):
        for right in accepted[index + 1 :]:
            if left.chunk.path.name != right.chunk.path.name and _negated_overlap(left.chunk.text, right.chunk.text):
                conflicts.append({"left_source": left.chunk.path.name, "right_source": right.chunk.path.name, "type": "textual_tension", "status": "needs_review"})
    if module_id == "medicina" and conflicts:
        accepted = [item.__class__(item.chunk, item.score, item.lexical_score, item.semantic_score, item.coverage, item.bm25_score, item.authority_score, item.freshness_score, item.provenance_score, item.support_score, 0.35, item.accepted, item.rejection_reason) for item in accepted]
    return EvidenceDecision(tuple(accepted), tuple(rejected), tuple(conflicts))
