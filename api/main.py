from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.bootstrap import bootstrap_registry
from routes.health import router as health_router
from routes.infra import router as infra_router
from routes.core import router as core_router
from routes.knowledge import router as knowledge_router
from routes.workflows import router as workflows_router
from routes.marketplace import router as marketplace_router
from routes.docs import router as docs_router
from routes.mcp import router as mcp_router
from routes.assistant import router as assistant_router
from routes.ai import router as ai_router
from routes.engine import router as engine_router
from routes.context import router as context_router
from routes.learning import router as learning_router
from routes.security import router as security_router
from config.settings import settings
from routes.zabbix import router as zabbix_router

app = FastAPI(title="SOFIA")
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

bootstrap_registry()

app.include_router(health_router)
app.include_router(infra_router)
app.include_router(zabbix_router)
app.include_router(core_router)
app.include_router(knowledge_router)
app.include_router(workflows_router)
app.include_router(marketplace_router)
app.include_router(docs_router)
app.include_router(mcp_router)
app.include_router(assistant_router)
app.include_router(ai_router)
app.include_router(engine_router)
app.include_router(context_router)
app.include_router(learning_router)
app.include_router(security_router)

@app.get("/")
def home():
    return {
        "projeto": "SOFIA",
        "status": "online",
        "engines": {
            "core": "/core",
            "knowledge": "/knowledge",
            "workflows": "/workflows",
            "marketplace": "/marketplace",
            "docs": "/docs",
            "zabbix": "/zabbix",
        },
        "zabbix": settings.ZABBIX_URL,
    }
