from __future__ import annotations

from pydantic import BaseModel, Field


class PlanModel(BaseModel):
    intent: str
    capabilities: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    needs_llm_reasoning: bool = True


class ContextModel(BaseModel):
    question: str
    intent: str
    plan: dict
    snapshot: dict = Field(default_factory=dict)
    knowledge: list[dict] = Field(default_factory=list)
    insights: list[dict] = Field(default_factory=list)
    history: list[dict] = Field(default_factory=list)
    evidence: list[dict] = Field(default_factory=list)
    risks: list[dict] = Field(default_factory=list)
    tools: dict = Field(default_factory=dict)
    summary: dict = Field(default_factory=dict)
    agent: dict = Field(default_factory=dict)
    hypothesis: dict = Field(default_factory=dict)


class AIAnswerModel(BaseModel):
    answer: str
    plan: dict
    context: dict
    llm_used: bool
    reasoning: dict = Field(default_factory=dict)
    critic: dict = Field(default_factory=dict)
    confidence: float = 0.0
    explainability: dict = Field(default_factory=dict)
    learning: dict = Field(default_factory=dict)