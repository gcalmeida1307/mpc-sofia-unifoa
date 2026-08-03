from fastapi import APIRouter
from pydantic import BaseModel, Field

from learning.service import learning_service

router = APIRouter(prefix="/learning", tags=["Learning"])


class LearningTrainRequest(BaseModel):
    question: str | None = Field(default=None, max_length=2000)


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
