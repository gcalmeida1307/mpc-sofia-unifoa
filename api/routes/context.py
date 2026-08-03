from fastapi import APIRouter

from ai.planner import build_plan
from context.builder import context_builder
from context.infrastructure import snapshot_service

router = APIRouter(prefix="/context", tags=["Context"])


@router.get("/snapshot")
def snapshot(refresh: bool = False):
    if refresh:
        return snapshot_service.refresh()
    return snapshot_service.get()


@router.get("/build")
def build(query: str):
    plan = build_plan(query)
    context = context_builder.build(query, plan)
    return {"query": query, "plan": plan, "context": context}
