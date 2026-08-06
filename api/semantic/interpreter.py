from __future__ import annotations

from typing import Any

from ai.client import ReasoningProvider
from semantic.examples import SEMANTIC_EXAMPLES
from semantic.fallback import deterministic_interpret
from semantic.models import SemanticQuery
from semantic.validator import validate_semantic_query


class SemanticGateway:
    def __init__(self, provider: ReasoningProvider | None = None):
        self.provider = provider or ReasoningProvider()

    def interpret(self, question: str) -> SemanticQuery:
        result: dict[str, Any] | None = self.provider.interpret(
            question=question,
            schema=SemanticQuery.model_json_schema(),
            examples=SEMANTIC_EXAMPLES,
        )
        if result:
            try:
                return validate_semantic_query(result.get("data", {}), provider=str(result.get("provider", "unknown")))
            except (ValueError, TypeError):
                pass
        return deterministic_interpret(question)


semantic_gateway = SemanticGateway()
