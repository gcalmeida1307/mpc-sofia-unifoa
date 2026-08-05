from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.service import openai_service
from services.postgres_store import postgres_store

router = APIRouter(prefix="/ai", tags=["AI"])


class AIAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/ask")
def ask(payload: AIAskRequest):
    postgres_store.add_message("user", payload.question, {"channel": "ai", "purpose": "training"})
    result = openai_service.answer(payload.question)
    answer = result.get("answer", "")
    postgres_store.add_message(
        "assistant",
        answer,
        {
            "channel": "ai",
            "purpose": "training",
            "learning_signature": result.get("learning", {}).get("signature"),
        },
    )
    return {
        "answer": answer,
        "plan": result.get("plan", {}),
        "reasoning": result.get("reasoning", {}),
        "critic": result.get("critic", {}),
        "llm_provider": result.get("critic", {}).get("provider", "none"),
        "confidence": result.get("confidence", 0.0),
        "explainability": result.get("explainability", {}),
        "learning": result.get("learning", {}),
        "llm_used": result.get("llm_used", False),
        "context": result.get("context", {}),
        "source": "openai-service",
    }
