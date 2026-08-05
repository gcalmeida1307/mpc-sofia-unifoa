from fastapi import APIRouter
from pydantic import BaseModel, Field
from fastapi import HTTPException, Request

from services.automation_graph import CONNECTOR_CATALOG, automation_graph_store

from services.workflows import list_n8n_templates, list_workflows, run_n8n_workflow, run_workflow

router = APIRouter(prefix="/workflows", tags=["Workflows"])


class WorkflowRunRequest(BaseModel):
    workflow_id: str
    event: dict | None = None


class N8NRunRequest(BaseModel):
    webhook: str
    event: dict | None = None


class AutomationGraphRequest(BaseModel):
    id: str | None = None
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)


def current_admin(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if not user or user.get("role") != "admin":
        raise HTTPException(403, "Perfil admin necessário")
    return user


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


@router.get("/automation/connectors")
def automation_connectors():
    return {"connectors": CONNECTOR_CATALOG}


@router.get("/automation/graphs")
def automation_graphs():
    return {"graphs": automation_graph_store.list()}


@router.post("/automation/graphs")
def automation_graph_save(payload: AutomationGraphRequest, request: Request):
    user = current_admin(request)
    try:
        saved = automation_graph_store.save(payload.name, payload.description, payload.nodes, payload.edges, user["id"], payload.id)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"status": "saved", **saved}


@router.post("/automation/graphs/{graph_id}/simulate")
def automation_graph_simulate(graph_id: str, request: Request):
    user = current_admin(request)
    try:
        return automation_graph_store.simulate(graph_id, user["id"])
    except KeyError:
        raise HTTPException(404, "Automação não encontrada")
