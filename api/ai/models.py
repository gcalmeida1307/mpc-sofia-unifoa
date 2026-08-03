from __future__ import annotations

from pydantic import BaseModel, Field


class PlanModel(BaseModel):
    intent: str
    tools: list[str] = Field(default_factory=list)
    needs_llm_reasoning: bool = True


class AIAnswerModel(BaseModel):
    answer: str
    plan: dict
    context: dict
    llm_used: bool