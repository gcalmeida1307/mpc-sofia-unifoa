from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from learning.service import learning_service
from services.learning_history import learning_history

router = APIRouter(prefix="/learning", tags=["Learning"])


class LearningTrainRequest(BaseModel):
    question: str | None = Field(default=None, max_length=2000)

class LearningFeedbackRequest(BaseModel):
    domain_id: str = Field(min_length=2, max_length=40)
    pattern_key: str = Field(min_length=1, max_length=120)
    verdict: str = Field(pattern="^(confirmed|rejected)$")
    evidence: dict = Field(default_factory=dict)


@router.post("/train")
def train(payload: LearningTrainRequest):
    insights = learning_service.learn(payload.question)
    return {
        "status": "trained",
        "insights": insights,
    }


@router.get("/insights")
def insights(limit: int = 10):
    return {
        "recent": learning_service.recent(limit=limit),
    }

@router.get("/status/{domain_id}")
def learning_status(domain_id: str):
    return learning_history.status(domain_id)

@router.post("/feedback")
def learning_feedback(payload: LearningFeedbackRequest, request: Request):
    return learning_history.record(payload.domain_id, payload.pattern_key, payload.verdict, payload.evidence, int(request.state.user["id"]))
