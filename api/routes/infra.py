from fastapi import APIRouter
from services.infrastructure import get_infrastructure_summary

router = APIRouter(prefix="/infra", tags=["Infraestrutura"])

@router.get("/resumo")
def resumo():
    return get_infrastructure_summary()
