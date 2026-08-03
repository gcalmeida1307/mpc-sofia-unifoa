from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.service import openai_service

router = APIRouter(prefix="/ai", tags=["AI"])


class AIAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/ask")
def ask(payload: AIAskRequest):
    result = openai_service.answer(payload.question)
    return {
        "answer": result.get("answer", ""),
        "plan": result.get("plan", {}),
        "llm_used": result.get("llm_used", False),
        "context": result.get("context", {}),
        "source": "openai-service",
    }
