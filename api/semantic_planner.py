"""Bounded semantic interpretation used before documentary retrieval.

The planner is intentionally narrower than an answer model.  The deterministic
router remains authoritative for scope, permissions, structured-data handling
and whether retrieval is required.  Ollama is the default interpreter; Claude
may be used as an explicitly authorized cloud fallback, receiving only a
redacted question and never the knowledge corpus.  Neither provider can change
the execution contract or write to the knowledge base.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from .privacy import ExternalRedaction, external_data_allowed
from .providers import Generation, generate
from .runtime_cache import get as runtime_cache_get
from .runtime_cache import set as runtime_cache_set

SEMANTIC_INTENTS = frozenset(
    {
        "DOCUMENT_RAG",
        "COMPARACAO_DOCUMENTOS",
        "COMPLEX_REASONING",
        "BUSCA_EXATA_LINHA",
        "LISTA_ELEMENTOS",
        "CONVERSA_DIRETA",
        "STRUCTURED_DATA",
        "EXECUCAO_MCP",
        "WRITING",
    }
)
_SEMANTIC_FAILURE_UNTIL = 0.0


@dataclass(frozen=True)
class SemanticPlan:
    """Safe, bounded interpretation that may enrich but never replace routing."""

    status: str = "deterministic"
    provider: str = "deterministic"
    intent: str = "DOCUMENT_RAG"
    topic: str = ""
    concepts: tuple[str, ...] = field(default_factory=tuple)
    search_terms: tuple[str, ...] = field(default_factory=tuple)
    entities: tuple[str, ...] = field(default_factory=tuple)
    subqueries: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0
    reason: str = ""

    def public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("concepts", "search_terms", "entities", "subqueries"):
            payload[key] = list(getattr(self, key))
        return payload

    @property
    def expanded_query(self) -> str:
        """Return only bounded, model-supplied vocabulary for local retrieval."""

        terms = list(dict.fromkeys((*self.concepts, *self.search_terms)))
        return " ".join(term for term in terms[:10] if term)

    def provider_context(self) -> str:
        """Expose the plan without raw history, identifiers or hidden reasoning."""

        if self.status not in {"ollama", "claude"} or not self.topic and not self.concepts:
            return ""
        fields = [
            f"tema={self.topic}" if self.topic else "",
            f"conceitos={', '.join(self.concepts[:8])}" if self.concepts else "",
            f"tarefas={'; '.join(self.subqueries[:6])}" if self.subqueries else "",
        ]
        origin = "local" if self.status == "ollama" else "externa autorizada"
        return f"Interpretação semântica auxiliar ({origin}; não é evidência documental): " + " | ".join(
            field for field in fields if field
        )


def _planner_mode() -> str:
    value = os.getenv("SOFIA_OLLAMA_SEMANTIC_PLANNER", "smart").strip().casefold()
    return value if value in {"off", "smart", "always"} else "smart"


def _should_plan(question: str, deterministic_plan: dict[str, Any], mode: str) -> bool:
    if mode == "off":
        return False
    if not bool(deterministic_plan.get("retrieval_required", True)):
        return False
    intent = str(deterministic_plan.get("intent", "DOCUMENT_RAG"))
    if intent in {"CONVERSA_DIRETA", "WRITING", "STRUCTURED_DATA", "EXECUCAO_MCP", "BUSCA_EXATA_LINHA"}:
        return False
    if mode == "always":
        return True
    normalized = str(question or "").casefold()
    words = re.findall(r"[\wÀ-ÿ]+", normalized)
    return (
        intent in {"COMPARACAO_DOCUMENTOS", "COMPLEX_REASONING"}
        or len(words) >= 14
        or len(re.findall(r"[?!]", normalized)) >= 2
        or any(
            marker in normalized
            for marker in (
                "compare",
                "comparar",
                "correlac",
                "infer",
                "conflito",
                "ambiguidade",
                "causa raiz",
                "o que temos em comum",
            )
        )
    )


def _clean_string(value: Any, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    # A planner result is metadata, not a second user prompt.  Keep control
    # characters and very long payloads out of logs, retrieval and providers.
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
    # The local planner may receive sensitive text, but its result is carried
    # into traces and (for cloud generation) into an auxiliary prompt.  Keep
    # the local interpretation useful while preventing identifiers from being
    # copied into planner metadata or sent to another provider.
    text = re.sub(
        r"(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b|\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
        "[identificador removido]",
        text,
    )
    text = re.sub(r"\b(?:\+?\d[\d ()-]{7,}\d)\b", "[telefone removido]", text)
    return text.strip()[:limit]


def _clean_list(value: Any, *, limit: int, item_limit: int = 100) -> tuple[str, ...]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return ()
    values: list[str] = []
    for item in value:
        cleaned = _clean_string(item, item_limit)
        if cleaned and cleaned.casefold() not in {previous.casefold() for previous in values}:
            values.append(cleaned)
        if len(values) >= limit:
            break
    return tuple(values)


def _json_payload(text: str) -> dict[str, Any] | None:
    value = str(text or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*|\s*```$", "", value, flags=re.IGNORECASE | re.DOTALL).strip()
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", value, flags=re.DOTALL)
        if not match:
            return None
        try:
            decoded = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return decoded if isinstance(decoded, dict) else None


def _fallback(deterministic_plan: dict[str, Any], reason: str) -> SemanticPlan:
    return SemanticPlan(
        status="deterministic",
        provider="deterministic",
        intent=str(deterministic_plan.get("intent", "DOCUMENT_RAG")),
        topic=_clean_string(deterministic_plan.get("theme", ""), 140),
        # Do not turn the deterministic router's token list into a second
        # retrieval query.  The normal policy expansion already owns that
        # vocabulary; duplicating it here can lower lexical precision when
        # Ollama is unavailable.
        concepts=(),
        search_terms=(),
        entities=_clean_list(deterministic_plan.get("entities"), limit=8),
        subqueries=_clean_list(deterministic_plan.get("subqueries"), limit=6, item_limit=180),
        confidence=0.0,
        reason=reason,
    )


def parse_plan(text: str, deterministic_plan: dict[str, Any], provider: str = "ollama") -> SemanticPlan:
    """Validate a bounded provider JSON response and fall back without raising."""

    payload = _json_payload(text)
    if not payload:
        return _fallback(deterministic_plan, f"{provider} não retornou um plano JSON válido")
    requested_intent = str(payload.get("intent", "")).strip().upper()
    intent = requested_intent if requested_intent in SEMANTIC_INTENTS else str(deterministic_plan.get("intent", "DOCUMENT_RAG"))
    deterministic_intent = str(deterministic_plan.get("intent", "DOCUMENT_RAG"))
    # The model cannot change safety-sensitive routing.  It can report a hint,
    # but the caller keeps the deterministic intent as the execution contract.
    if deterministic_intent in SEMANTIC_INTENTS:
        intent = deterministic_intent
    confidence = payload.get("confidence", 0.0)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.0
    return SemanticPlan(
        status=provider,
        provider=provider,
        intent=intent,
        topic=_clean_string(payload.get("topic"), 140),
        concepts=_clean_list(payload.get("concepts"), limit=8),
        search_terms=_clean_list(payload.get("search_terms"), limit=8),
        entities=_clean_list(payload.get("entities"), limit=8),
        subqueries=_clean_list(payload.get("subqueries"), limit=6, item_limit=180),
        confidence=confidence,
        reason=(
            "plano semântico local validado; roteamento determinístico preservado"
            if provider == "ollama"
            else "plano semântico externo redigido e validado; roteamento determinístico preservado"
        ),
    )


def _prompt(module_id: str, question: str, deterministic_plan: dict[str, Any]) -> tuple[str, str]:
    system = (
        "Você é um interpretador semântico local da plataforma SOFIA. "
        "Não responda à pergunta, não consulte documentos, não invente fatos e não produza explicações. "
        "Retorne somente JSON válido com as chaves intent, topic, concepts, search_terms, entities, subqueries e confidence. "
        "Use listas curtas. Não repita nomes, e-mails, CPF, matrícula, dados clínicos ou outros identificadores; "
        "substitua qualquer identificador por uma categoria genérica. "
        "O intent é apenas uma sugestão: o sistema manterá o contrato determinístico de execução."
    )
    prompt = json.dumps(
        {
            "module": module_id,
            "question": question[:3000],
            "deterministic_plan": {
                "intent": deterministic_plan.get("intent", "DOCUMENT_RAG"),
                "strategy": deterministic_plan.get("strategy", "FACT_LOOKUP"),
                "theme": deterministic_plan.get("theme", ""),
                "source_profile": deterministic_plan.get("source_profile", ""),
            },
        },
        ensure_ascii=False,
    )
    return system, prompt


def _semantic_provider_mode() -> str:
    value = os.getenv("SOFIA_SEMANTIC_PROVIDER", "auto").strip().casefold()
    return value if value in {"auto", "ollama", "claude"} else "auto"


def _cloud_semantic_allowed(external_allowed: bool | None) -> bool:
    return external_data_allowed() if external_allowed is None else bool(external_allowed)


def _provider_candidates(mode: str, external_allowed: bool | None) -> tuple[str, ...]:
    if mode == "ollama":
        return ("ollama",)
    if mode == "claude":
        return ("claude",) if _cloud_semantic_allowed(external_allowed) and os.getenv("ANTHROPIC_API_KEY") else ()
    candidates = ["ollama"]
    if _cloud_semantic_allowed(external_allowed) and os.getenv("ANTHROPIC_API_KEY"):
        candidates.append("claude")
    return tuple(candidates)


async def interpret(
    module_id: str,
    question: str,
    deterministic_plan: dict[str, Any],
    external_allowed: bool | None = None,
) -> SemanticPlan:
    """Interpret a complex documentary query with a hard time bound.

    The deterministic route always runs first.  Claude is only a fallback for
    semantic understanding when external data use was explicitly allowed; it
    receives a redacted question and its output remains bounded metadata.
    """

    fallback = _fallback(deterministic_plan, "roteamento determinístico suficiente para esta consulta")
    mode = _planner_mode()
    if not _should_plan(question, deterministic_plan, mode):
        return fallback
    semantic_mode = _semantic_provider_mode()
    candidates = _provider_candidates(semantic_mode, external_allowed)
    if not candidates:
        return _fallback(deterministic_plan, "Claude semântico não está autorizado ou configurado")
    # Interpretation is safe to cache in-process because the key is a digest,
    # the value is bounded metadata, and no prompt or raw question is written
    # to disk.  Corpus changes do not invalidate this cache: interpretation is
    # about the request, while retrieval has its own corpus-stamped cache.
    cache_key = (
        module_id,
        hashlib.sha256(question.encode("utf-8", "ignore")).hexdigest(),
        str(deterministic_plan.get("intent", "DOCUMENT_RAG")),
        os.getenv("OLLAMA_MODEL", "qwen3.5:4b"),
        os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        semantic_mode,
        bool(_cloud_semantic_allowed(external_allowed)),
        mode,
    )
    cached = runtime_cache_get("semantic-planner", cache_key)
    if isinstance(cached, SemanticPlan):
        return cached
    global _SEMANTIC_FAILURE_UNTIL
    if candidates == ("ollama",) and time.monotonic() < _SEMANTIC_FAILURE_UNTIL:
        return _fallback(deterministic_plan, "circuit breaker local: Ollama semântico indisponível recentemente")
    try:
        timeout = max(0.4, min(8.0, float(os.getenv("SOFIA_SEMANTIC_PLANNER_TIMEOUT_SECONDS", "1.8"))))
    except ValueError:
        timeout = 1.8
    system, prompt = _prompt(module_id, question, deterministic_plan)
    last_error = ""
    for candidate in candidates:
        if candidate == "claude":
            # Semantic interpretation is not an answer and must not carry raw
            # identifiers to a cloud provider.  The local retriever remains
            # the only authority for document facts.
            prompt_for_provider = ExternalRedaction().clean(prompt)
        else:
            prompt_for_provider = prompt
        try:
            generation: Generation = await asyncio.wait_for(
                generate(
                    candidate,
                    system,
                    prompt_for_provider,
                    [],
                    max_output_tokens=256,
                    timeout_seconds=timeout,
                ),
                timeout=timeout + 0.2,
            )
            parsed = parse_plan(generation.answer, deterministic_plan, provider=candidate)
            if parsed.status != candidate:
                last_error = parsed.reason
                continue
            if candidate == "ollama":
                _SEMANTIC_FAILURE_UNTIL = 0.0
            runtime_cache_set("semantic-planner", cache_key, parsed)
            return parsed
        except Exception as exc:  # noqa: BLE001
            last_error = f"{candidate} semântico indisponível: {type(exc).__name__}"
            if candidate == "ollama":
                try:
                    cooldown = max(5.0, min(300.0, float(os.getenv("SOFIA_SEMANTIC_PLANNER_FAILURE_COOLDOWN_SECONDS", "30"))))
                except ValueError:
                    cooldown = 30.0
                _SEMANTIC_FAILURE_UNTIL = time.monotonic() + cooldown
    return _fallback(deterministic_plan, last_error or "interpretação semântica indisponível")
