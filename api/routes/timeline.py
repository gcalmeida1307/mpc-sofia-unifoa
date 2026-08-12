from fastapi import APIRouter, HTTPException, Query, Request

from services.temporal_intelligence import WINDOWS, temporal_intelligence

router=APIRouter(prefix="/timeline",tags=["Temporal Intelligence"])


@router.get("/{domain_id}")
def timeline(domain_id:str,request:Request,window:int=Query(default=60)):
    if window not in WINDOWS:raise HTTPException(422,"Janela inválida")
    return temporal_intelligence.story(domain_id,window)
