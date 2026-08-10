from fastapi import APIRouter

from config.settings import settings
from core.registry import registry
from core.event_bus import event_bus
from core.domain_registry import domain_registry

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
    autonomy = registry.get("autonomy_scheduler") if registry.has("autonomy_scheduler") else None
    domain_health = []
    for definition in domain_registry.definitions():
        checks = []
        for check in definition.health_checks():
            try:
                checks.append(check())
            except Exception as exc:
                checks.append({"name": getattr(check, "__name__", "health"), "status": "error", "detail": str(exc)})
        domain_health.append({"domain_id": definition.domain_id, "checks": checks})
    return {
        "modules": registry.list_modules(),
        "services": registry.get_snapshot().get("services", []),
        "event_subscribers": event_bus.snapshot(),
        "domains": domain_registry.catalog(),
        "domain_health": domain_health,
        "scheduler": {
            "enabled": scheduler is not None,
            "interval_seconds": getattr(scheduler, "interval_seconds", None),
        },
        "autonomy": {
            "enabled": autonomy is not None,
            "interval_seconds": getattr(autonomy, "interval_seconds", None),
        },
    }


@router.get("/settings")
def settings_snapshot():
    return settings.snapshot(masked=True)
