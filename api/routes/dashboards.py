from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from services.dashboard_layouts import dashboard_layout_store


router=APIRouter(prefix="/dashboards",tags=["Dashboards"])


class LayoutRequest(BaseModel):layout:dict


@router.get("/layout")
def get_layout(request:Request):return dashboard_layout_store.get(int(request.state.user["id"]))


@router.put("/layout")
def save_layout(payload:LayoutRequest,request:Request):
    try:return dashboard_layout_store.save(int(request.state.user["id"]),payload.layout)
    except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
