"""Generic, auditable response pipeline for the SOFIA CORE.

This module deliberately knows nothing about SAAE, Zabbix, ENAP or any other
institutional topic.  It only turns the validated query plan and the accepted
retrieval result into the common pipeline contract:

    classify -> hybrid retrieval -> semantic reranking -> evidence gate
    -> grounded synthesis or evidence gap -> citation validation

Domain packages may improve retrieval, but they must not become answer
generators.  Keeping this boundary small prevents every new user question
from adding another special case to ``orchestration.py``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .retrieval import Evidence, RetrievalResult, normalize

CORE_INTENTS = frozenset(
    {"CONVERSATION", "DOCUMENT_RAG", "MULTI_DOCUMENT", "STRUCTURED_DATA"}
)


@dataclass(frozen=True)
class CorePipelinePlan:
    """Small execution contract shared by retrieval, generation and audit."""

    intent: str
    retrieval_required: bool
    strategy: str
    source_hints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.intent not in CORE_INTENTS:
            raise ValueError(f"intenção CORE inválida: {self.intent}")

    def public_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "retrieval_required": self.retrieval_required,
            "strategy": self.strategy,
            "source_hints": list(self.source_hints),
            "stages": [
                "classify_intent",
                "hybrid_retrieval",
                "semantic_reranking",
                "evidence_gate",
                "grounded_synthesis_or_gap",
                "citation_validation",
            ],
        }


@dataclass(frozen=True)
class EvidenceGate:
    """Result of the generic evidence boundary."""

    status: str
    sufficient: bool
    accepted_count: int
    source_count: int
    missing_sources: tuple[str, ...]
    confidence: float
    reason: str

    def public_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "sufficient": self.sufficient,
            "accepted_count": self.accepted_count,
            "source_count": self.source_count,
            "missing_sources": list(self.missing_sources),
            "confidence": self.confidence,
            "reason": self.reason,
        }


def plan_from_query_plan(query_plan: Any) -> CorePipelinePlan:
    """Map the legacy query taxonomy to the four CORE intentions.

    The old, more detailed intent labels remain available for compatibility,
    but they no longer decide how a response is written.
    """

    intent = str(getattr(query_plan, "intent", "DOCUMENT_RAG"))
    strategy = str(getattr(query_plan, "strategy", "FACT_LOOKUP"))
    retrieval_required = bool(getattr(query_plan, "retrieval_required", True))
    hints = getattr(query_plan, "source_hints", ()) or ()
    if intent == "CONVERSA_DIRETA" or not retrieval_required:
        core_intent = "CONVERSATION"
    elif intent == "STRUCTURED_DATA" or strategy == "STRUCTURED_DATA":
        core_intent = "STRUCTURED_DATA"
    elif intent in {"COMPARACAO_DOCUMENTOS", "COMPLEX_REASONING"} or strategy in {
        "MULTI_DOCUMENT_SYNTHESIS",
        "CONCEPT_COMPARISON",
        "MULTI_HOP",
        "RCA_INVESTIGATION",
    }:
        core_intent = "MULTI_DOCUMENT"
    else:
        core_intent = "DOCUMENT_RAG"
    return CorePipelinePlan(core_intent, retrieval_required, strategy, tuple(str(item) for item in hints))


def judge_result(result: RetrievalResult) -> EvidenceGate:
    """Expose one generic gate instead of making callers infer it from scores."""

    accepted = len(result.evidence)
    sources = len(result.sources)
    if result.has_quality_evidence:
        return EvidenceGate(
            "sufficient",
            True,
            accepted,
            sources,
            tuple(result.missing_sources),
            round(float(result.judge_confidence), 4),
            "evidência aceita pelo Evidence Judge",
        )
    if accepted and result.missing_sources:
        return EvidenceGate(
            "partial",
            False,
            accepted,
            sources,
            tuple(result.missing_sources),
            round(float(result.judge_confidence), 4),
            "há trechos aceitos, mas falta uma fonte ou parte exigida",
        )
    return EvidenceGate(
        "gap",
        False,
        accepted,
        sources,
        tuple(result.missing_sources),
        round(float(result.judge_confidence), 4),
        "nenhuma evidência local suficiente passou pelo gate",
    )


_FRAGMENT_ENDINGS = {
    "a",
    "ao",
    "aos",
    "as",
    "até",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "entre",
    "mais",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "ou",
    "para",
    "pela",
    "pelas",
    "pelo",
    "pelos",
    "por",
    "que",
    "sem",
    "sobre",
    "uma",
    "um",
}


def _sentences(text: str) -> list[str]:
    values: list[str] = []
    for raw in re.split(r"(?:\n+|(?<=[.!?])\s+|•+)", text):
        value = re.sub(r"\s+", " ", raw).strip(" -•\t")
        if len(value) < 32:
            continue
        last = normalize(value).rstrip(" .:;!?…").split()
        if last and last[-1] in _FRAGMENT_ENDINGS:
            continue
        if value.casefold().startswith(("documento:", "localização:", "localizacao:", "seção:", "secao:", "tipo:")):
            continue
        values.append(value)
    return values


def _source_label(source: str) -> str:
    normalized = normalize(source)
    if "saae" in normalized:
        return "acordo SAAE"
    if "vade" in normalized or "mecum" in normalized:
        return "Vade Mecum"
    return f"documento {source}"


def _rank_sentences(question: str, item: Evidence) -> list[str]:
    question_terms = {
        term
        for term in re.findall(r"[\wÀ-ÿ]{4,}", normalize(question))
        if term not in {"qual", "quais", "como", "sobre", "documento", "arquivo", "fonte"}
    }
    scored: list[tuple[float, str]] = []
    for sentence in _sentences(item.chunk.text):
        terms = set(re.findall(r"[\wÀ-ÿ]{4,}", normalize(sentence)))
        scored.append((float(len(question_terms & terms)) + float(item.score), sentence))
    scored.sort(key=lambda value: value[0], reverse=True)
    return [sentence for _, sentence in scored]


def grouped_evidence(result: RetrievalResult, question: str, max_chars: int = 24000) -> str:
    """Build the only evidence context that a synthesizer should receive.

    Evidence is grouped by source and location. Rejected candidates and the
    flattened corpus are intentionally excluded, so a model cannot confuse a
    menu, a nearby page or a CSV row with the accepted documentary premise.
    """

    grouped: dict[str, list[tuple[Evidence, str]]] = {}
    for item in result.evidence:
        for sentence in _rank_sentences(question, item)[:3]:
            grouped.setdefault(item.chunk.path.name, []).append((item, sentence))
    blocks: list[str] = []
    consumed = 0
    for source, entries in grouped.items():
        lines = [f"DOCUMENTO: {source}"]
        seen: set[str] = set()
        for item, sentence in entries:
            key = normalize(sentence)
            if key in seen:
                continue
            seen.add(key)
            locator = item.chunk.locator or (
                f"página {item.chunk.page}" if item.chunk.page else f"trecho {item.chunk.ordinal}"
            )
            lines.append(f"LOCALIZAÇÃO: {locator}\n{sentence}")
        block = "\n".join(lines)
        if len("\n\n---\n\n".join(blocks + [block])) > max_chars and blocks:
            break
        blocks.append(block)
        consumed += len(block)
        if consumed >= max_chars:
            break
    return "\n\n---\n\n".join(blocks)


def is_complete_answer(answer: str) -> bool:
    """Reject the mutilated provider/local fragments seen in prior responses."""

    meaningful = [line.strip() for line in answer.splitlines() if line.strip()]
    if not meaningful:
        return False
    body = [line.lstrip("-*• ").strip() for line in meaningful]
    prose = [line for line in body if len(line) >= 24 and not line.endswith(":")]
    if not prose:
        return False
    final = normalize(prose[-1]).rstrip(" .:;!?…")
    if not final:
        return False
    return final.split()[-1] not in _FRAGMENT_ENDINGS


def grounded_fallback(result: RetrievalResult, question: str, language: str = "pt-BR") -> str:
    """Compose a coherent, source-grouped floor when no LLM is available."""

    if not result.evidence:
        messages = {
            "pt-BR": "Não encontrei evidência documental suficiente no módulo para responder com segurança.",
            "en": "I did not find enough documentary evidence in this module to answer safely.",
            "es": "No encontré evidencia documental suficiente en este módulo para responder con seguridad.",
        }
        return messages.get(language, messages["pt-BR"])

    grouped: dict[str, list[tuple[Evidence, str]]] = {}
    for item in result.evidence:
        for sentence in _rank_sentences(question, item)[:2]:
            grouped.setdefault(item.chunk.path.name, []).append((item, sentence))

    if language == "en":
        opening = "The retrieved documents support the following reading:"
        missing = "I did not find specific passages for the remaining part of the question in the local base."
    elif language == "es":
        opening = "Los documentos recuperados permiten la siguiente lectura:"
        missing = "No encontré fragmentos específicos para la parte restante de la pregunta en la base local."
    else:
        opening = "Os documentos recuperados permitem a seguinte leitura:"
        missing = "Não identifiquei trechos específicos para a parte restante da pergunta na base local."

    blocks = [opening]
    if len(grouped) > 1 and (result.subqueries or len(result.required_sources) > 1):
        if language == "pt-BR":
            blocks.append("As fontes tratam de dois pontos diferentes da pergunta; a leitura abaixo mantém cada documento separado antes de relacioná-los.")
        elif language == "en":
            blocks.append("The sources address different parts of the question; the reading below keeps each document separate before relating them.")
        else:
            blocks.append("Las fuentes tratan puntos diferentes de la pregunta; la lectura siguiente mantiene cada documento separado antes de relacionarlos.")
    for source, entries in grouped.items():
        selected: list[str] = []
        locators: list[str] = []
        for item, sentence in entries:
            if normalize(sentence) in {normalize(value) for value in selected}:
                continue
            selected.append(sentence)
            locator = item.chunk.locator or (
                f"página {item.chunk.page}" if item.chunk.page else f"trecho {item.chunk.ordinal}"
            )
            if locator not in locators:
                locators.append(locator)
        if selected:
            label = _source_label(source)
            blocks.append(f"No {label} ({', '.join(locators[:2])}), consta que " + " ".join(selected[:2]))

    if len(grouped) > 1 and (result.subqueries or len(result.required_sources) > 1):
        if language == "pt-BR":
            blocks.append("Os trechos recuperados não informam, por si só, se a regra de um ponto autoriza ou afasta a regra do outro; essa relação exige a norma específica aplicável.")
        elif language == "en":
            blocks.append("The retrieved passages do not, by themselves, say whether the rule for one point authorizes or displaces the rule for the other; that relation requires the applicable specific rule.")
        else:
            blocks.append("Los fragmentos recuperados no informan por sí solos si la regla de un punto autoriza o desplaza la del otro; esa relación exige la norma específica aplicable.")

    if result.missing_sources or result.unanswered_queries:
        blocks.append(missing)
    elif result.conflicts:
        if language == "pt-BR":
            blocks.append("Há uma divergência textual entre trechos recuperados; ela precisa ser analisada à luz da versão e do contexto de cada documento.")
        elif language == "en":
            blocks.append("The retrieved passages contain a textual divergence; it must be reviewed against each document's version and context.")
        else:
            blocks.append("Los fragmentos recuperados contienen una divergencia textual; debe revisarse según la versión y el contexto de cada documento.")
    return "\n\n".join(blocks)
