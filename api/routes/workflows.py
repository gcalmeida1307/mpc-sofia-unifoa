from fastapi import APIRouter
from pydantic import BaseModel

from services.workflows import list_n8n_templates, list_workflows, run_n8n_workflow, run_workflow

router = APIRouter(prefix="/workflows", tags=["Workflows"])


class WorkflowRunRequest(BaseModel):
    workflow_id: str
    event: dict | None = None


class N8NRunRequest(BaseModel):
    webhook: str
    event: dict | None = None


@router.get("/")
def list_route():
    return list_workflows()


@router.post("/run")
def run(payload: WorkflowRunRequest):
    return run_workflow(payload.workflow_id, payload.event or {})


@router.get("/n8n/templates")
def n8n_templates():
    return list_n8n_templates()


@router.post("/n8n/run")
def n8n_run(payload: N8NRunRequest):
    return run_n8n_workflow(payload.webhook, payload.event or {})
