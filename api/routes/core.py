from fastapi import APIRouter

from config.settings import settings
from core.registry import registry
from core.event_bus import event_bus

router = APIRouter(prefix="/core", tags=["Core"])


@router.get("/registry")
def registry_snapshot():
    return registry.get_snapshot()


@router.get("/modules")
def modules():
    return {"modules": registry.list_modules()}


@router.get("/kernel")
def kernel_status():
    return {
        "modules": registry.list_modules(),
        "services": registry.get_snapshot().get("services", []),
        "event_subscribers": event_bus.snapshot(),
    }


@router.get("/settings")
def settings_snapshot():
    return settings.snapshot(masked=True)
