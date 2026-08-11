from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from services.domain_catalog import THEMES, declarative_domain_catalog


router=APIRouter(prefix="/domains",tags=["Domains"])


class DomainInstallRequest(BaseModel):
    domain_id:str=Field(min_length=3,max_length=40)
    display_name:str=Field(min_length=3,max_length=80)
    description:str=Field(default="",max_length=500)
    purpose:str=Field(min_length=10,max_length=1000)
    entities:list[str]=Field(default_factory=list,max_length=30)
    metrics:list[str]=Field(default_factory=list,max_length=30)
    source_url:str|None=Field(default=None,max_length=500)
    refresh_seconds:int=Field(default=86400,ge=3600,le=2592000)
    theme:str=Field(default="ocean",max_length=20)


@router.get("")
def list_domains():return {"domains":declarative_domain_catalog.list()}


@router.post("")
def install_domain(payload:DomainInstallRequest,request:Request):
    try:return declarative_domain_catalog.install(payload.model_dump(),int(request.state.user["id"]))
    except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc)) from exc


@router.get("/experience/catalog")
def experience_catalog():return {"domains":declarative_domain_catalog.experiences(),"themes":THEMES}


@router.get("/{domain_id}")
def domain_manifest(domain_id:str):
    domain=declarative_domain_catalog.get(domain_id)
    if not domain:raise HTTPException(status_code=404,detail="domínio não encontrado")
    return domain


@router.get("/{domain_id}/status")
def domain_status(domain_id:str):
    domain=declarative_domain_catalog.get(domain_id)
    if not domain:raise HTTPException(status_code=404,detail="domínio não encontrado")
    return {"domain_id":domain_id,"status":domain["status"] if domain["enabled"] else "disabled","checks":domain.get("provisioning",{})}


@router.get("/{domain_id}/search")
def domain_search(domain_id:str,query:str=Query(min_length=2,max_length=500)):
    try:return declarative_domain_catalog.search(domain_id,query)
    except KeyError as exc:raise HTTPException(status_code=404,detail="domínio inexistente ou desabilitado") from exc


@router.delete("/{domain_id}")
def disable_domain(domain_id:str):
    if not declarative_domain_catalog.set_enabled(domain_id,False):raise HTTPException(status_code=404,detail="domínio não encontrado")
    return {"domain_id":domain_id,"status":"disabled"}
