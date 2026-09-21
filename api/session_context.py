"""Bounded session context for the intelligence pipeline.

The browser may send the whole visible conversation on every request.  That
conversation is useful for resolving a follow-up, but it is not a knowledge
source and must not become an ever-growing prompt, retrieval query or audit
record.  This module keeps only a small, request-scoped window.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MAX_HISTORY_TURNS = 6
MAX_TURN_CHARS = 1_600
MAX_HISTORY_CHARS = 8_000
MAX_EXTRA_CONTEXT_CHARS = 12_000


def bound_text(value: Any, limit: int) -> str:
    """Keep the beginning and end of a value without creating a huge prompt."""

    text = str(value or "").replace("\x00", " ").strip()
    if len(text) <= limit:
        return text
    # The beginning normally contains the answer/topic and the end often has
    # source locators.  Keeping both is more useful than a hard prefix cut.
    tail = min(320, max(80, limit // 5))
    head = max(0, limit - tail - 32)
    return f"{text[:head].rstrip()}\n[… contexto resumido …]\n{text[-tail:].lstrip()}"


def bound_history(history: list[dict[str, str]] | None) -> list[dict[str, str]]:
    """Return a small, role-filtered history for this request only."""

    if not history:
        return []
    selected: list[dict[str, str]] = []
    total = 0
    for item in reversed(history):
        role = str(item.get("role", "")).strip().casefold()
        content = bound_text(item.get("content", ""), MAX_TURN_CHARS)
        if role not in {"user", "assistant"} or not content:
            continue
        cost = len(content)
        if selected and (len(selected) >= MAX_HISTORY_TURNS or total + cost > MAX_HISTORY_CHARS):
            break
        selected.append({"role": role, "content": content})
        total += cost
    selected.reverse()
    return selected


@dataclass(frozen=True)
class SessionContext:
    """Request-scoped context; it is never a knowledge-base artifact."""

    history: list[dict[str, str]]
    extra_context: str

    @classmethod
    def from_request(
        cls,
        history: list[dict[str, str]] | None,
        extra_context: str | None = None,
    ) -> SessionContext:
        return cls(
            history=bound_history(history),
            extra_context=bound_text(extra_context, MAX_EXTRA_CONTEXT_CHARS),
        )
