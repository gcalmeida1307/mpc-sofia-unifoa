from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from connectors.zabbix import ZabbixConnector
from services.zabbix_investigator import zabbix_investigator

router = APIRouter(prefix="/zabbix", tags=["Zabbix"])


class GroupCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)

class InvestigationRequest(BaseModel):
    question: str = Field(min_length=3,max_length=1000)
    hours: int = Field(default=2,ge=1,le=24)
    recurrence_days: int = Field(default=7,ge=1,le=30)
    max_problems: int = Field(default=20,ge=1,le=50)

@router.post("/investigate")
def investigate(payload: InvestigationRequest):
    try:return zabbix_investigator.investigate(payload.question,hours=payload.hours,recurrence_days=payload.recurrence_days,max_problems=payload.max_problems)
    except Exception as exc:raise HTTPException(status_code=502,detail=f"Falha na investigação Zabbix: {exc}") from exc


@router.get("/groups")
def groups(limit: int = 200):
    return {"groups": ZabbixConnector().list_groups(limit=max(1, min(limit, 500)))}


@router.get("/groups/metrics")
def group_metrics(limit: int = 200):
    connector = ZabbixConnector()
    groups = connector.list_groups(limit=max(1, min(limit, 500)))
    problems = connector.list_active_problems(limit=200)
    active_by_group: dict[str, int] = {}
    for problem in problems:
        for group in problem.get("groups", []) or []:
            active_by_group[group] = active_by_group.get(group, 0) + 1
    metrics = [
        {
            **group,
            "active_problems": active_by_group.get(group["name"], 0),
            "problem_percentage": round((active_by_group.get(group["name"], 0) / max(group["hosts"], 1)) * 100, 2),
        }
        for group in groups
    ]
    return {"groups": metrics, "definition": "active problems per host; not total configured triggers"}


@router.post("/groups")
def create_group(payload: GroupCreateRequest):
    try:
        return {"status": "created", "group": ZabbixConnector().create_group(payload.name.strip())}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
