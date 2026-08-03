from __future__ import annotations

from context.builder import context_builder


def build_context(question: str, tool_names: list[str]) -> dict:
    plan = {
        "intent": "compat-context",
        "tools": tool_names,
        "needs_llm_reasoning": False,
    }
    return context_builder.build(question, plan)
