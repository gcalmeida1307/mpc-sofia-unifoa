from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.service import openai_service
from ai.domain_policy import OUT_OF_SCOPE_MESSAGE, is_it_question
from services.knowledge import search_knowledge
from services.postgres_store import postgres_store

router = APIRouter(prefix="/ai", tags=["AI"])


class AIAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/ask")
def ask(payload: AIAskRequest):
    if not is_it_question(payload.question):
        return {
            "answer": OUT_OF_SCOPE_MESSAGE,
            "plan": {"intent": "out_of_scope", "tools": []},
            "reasoning": {"mode": "domain_guard"},
            "critic": {"approved": True, "provider": "none"},
            "llm_provider": "none",
            "confidence": 1.0,
            "explainability": {"domain": "outside_information_technology"},
            "learning": {"stored": False, "reason": "out_of_scope"},
            "llm_used": False,
            "context": {},
            "source": "domain-policy",
        }

    postgres_store.add_message("user", payload.question, {"channel": "ai", "purpose": "training"})
    offline = search_knowledge(payload.question)
    results = offline.get("results", []) if isinstance(offline, dict) else []
    best = results[0] if results else None
    if isinstance(best, dict) and float(best.get("score", 0.0) or 0.0) >= 0.55:
        snippet = str(best.get("snippet", "")).strip()
        source = str(best.get("source", "base offline")).strip()
        answer = f"Segundo a base offline ({source}): {snippet}"
        postgres_store.add_message("assistant", answer, {"channel": "ai", "purpose": "training", "source": "offline_knowledge"})
        return {
            "answer": answer,
            "plan": {"intent": "offline_knowledge", "tools": ["knowledge.search"]},
            "reasoning": {"mode": "offline_first"},
            "critic": {"approved": True, "provider": "offline"},
            "llm_provider": "none",
            "confidence": float(best.get("score", 0.0)),
            "explainability": {"domain": "information_technology", "knowledge_source": source},
            "learning": {"stored": True, "reused": True},
            "llm_used": False,
            "context": {"knowledge": results[:3]},
            "source": "offline-knowledge",
        }

    result = openai_service.answer(payload.question)
    answer = result.get("answer", "")
    postgres_store.add_message(
        "assistant", answer,
        {"channel": "ai", "purpose": "training", "learning_signature": result.get("learning", {}).get("signature")},
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
        "source": "claude-learning-pipeline",
    }
