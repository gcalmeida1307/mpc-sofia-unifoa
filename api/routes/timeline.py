from fastapi import APIRouter, HTTPException, Query, Request

from services.temporal_intelligence import WINDOWS, temporal_intelligence

router=APIRouter(prefix="/timeline",tags=["Temporal Intelligence"])


@router.get("/{domain_id}")
def timeline(domain_id:str,request:Request,window:int=Query(default=60)):
    if window not in WINDOWS:raise HTTPException(422,"Janela inválida")
    user=request.state.user
    if user.get("role")!="admin":
        from services.auth import auth_service
        if domain_id not in {item["domain_id"] for item in auth_service.domain_access(int(user["id"]))}:raise HTTPException(403,"Sem acesso a este domínio")
    return temporal_intelligence.story(domain_id,window)
