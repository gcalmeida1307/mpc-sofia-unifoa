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
    scheduler = registry.get("snapshot_scheduler") if registry.has("snapshot_scheduler") else None
    return {
        "modules": registry.list_modules(),
        "services": registry.get_snapshot().get("services", []),
        "event_subscribers": event_bus.snapshot(),
        "scheduler": {
            "enabled": scheduler is not None,
            "interval_seconds": getattr(scheduler, "interval_seconds", None),
        },
    }


@router.get("/settings")
def settings_snapshot():
    return settings.snapshot(masked=True)
