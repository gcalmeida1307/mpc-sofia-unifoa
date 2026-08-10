from fastapi import APIRouter
from services.infrastructure import get_infrastructure_summary
from services.behavior_patterns import behavior_pattern_analyzer

router = APIRouter(prefix="/infra", tags=["Infraestrutura"])

@router.get("/resumo")
def resumo():
    return get_infrastructure_summary()


@router.get("/patterns")
def patterns():
    return behavior_pattern_analyzer.patterns(force=False)
