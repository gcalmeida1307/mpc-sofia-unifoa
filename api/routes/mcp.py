from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from core.registry import registry
from services.mcp_server import mcp_server

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/tools")
def tools() -> dict[str, Any]:
    return {
        "provider": "SOFIA MCP",
        "registered_modules": registry.list_modules(),
        "capabilities": registry.get_snapshot()["capabilities"],
    }


@router.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "provider": "SOFIA MCP", "modules": registry.list_modules()}


@router.post("")
async def rpc(request: Request) -> Response:
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise HTTPException(status_code=415, detail="MCP requests must use application/json")
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    response = mcp_server.handle(payload)
    if response is None:
        return Response(status_code=202)
    return JSONResponse(response)


@router.post("/rpc")
async def rpc_compat(request: Request) -> Response:
    return await rpc(request)
