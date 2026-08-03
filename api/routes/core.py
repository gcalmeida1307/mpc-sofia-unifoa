from fastapi import APIRouter

from core.bootstrap import bootstrap_registry
from core.registry import registry

router = APIRouter(prefix="/core", tags=["Core"])


@router.get("/registry")
def registry_snapshot():
    return bootstrap_registry()


@router.get("/modules")
def modules():
    return {"modules": registry.list_modules()}
