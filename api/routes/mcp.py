from fastapi import APIRouter

from core.registry import registry

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/tools")
def tools():
    return {
        "provider": "SOFIA MCP",
        "registered_modules": registry.list_modules(),
        "capabilities": registry.get_snapshot()["capabilities"],
    }


@router.get("/health")
def health():
    return {
        "status": "ok",
        "provider": "SOFIA MCP",
        "modules": registry.list_modules(),
    }
