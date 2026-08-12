from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from services.investigations import investigation_service

router = APIRouter(prefix="/investigations", tags=["Investigations"])

class CreateInvestigation(BaseModel):
    domain_id: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=3, max_length=200)

class AddItem(BaseModel):
    type: str = Field(pattern="^(entity|event|hypothesis|evidence)$")
    payload: dict
    verdict: str | None = Field(default=None, pattern="^(confirmed|rejected|pending)$")

@router.post("")
def create(payload: CreateInvestigation, request: Request):
    return investigation_service.create(payload.domain_id, payload.title, int(request.state.user["id"]))

@router.get("/{investigation_id}")
def get(investigation_id: str):
    try: return investigation_service.get(investigation_id)
    except KeyError as exc: raise HTTPException(404, "investigação não encontrada") from exc

@router.post("/{investigation_id}/items")
def add(investigation_id: str, payload: AddItem, request: Request):
    try: return investigation_service.add(investigation_id, payload.type, payload.payload, int(request.state.user["id"]), payload.verdict)
    except Exception as exc:
        if "foreign key" in str(exc).lower(): raise HTTPException(404, "investigação não encontrada") from exc
        raise
