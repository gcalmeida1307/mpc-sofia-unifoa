from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from core.bootstrap import bootstrap_registry
from core.event_bus import event_bus
from core.event_handlers import register_default_event_handlers
from core.registry import registry


class Application:
    def __init__(self):
        self.settings = settings
        self.registry = registry
        self.event_bus = event_bus

    async def startup(self) -> None:
        # Kernel dependencies are registered once and reused via registry.get(...).
        self.registry.clear()
        self.event_bus.clear()

        snapshot = bootstrap_registry()
        self.registry.register_service("settings", self.settings)
        self.registry.register_service("event_bus", self.event_bus)
        self.registry.register_service("registry_snapshot", snapshot)
        register_default_event_handlers(self.event_bus)

        for module_name in self.registry.list_modules():
            module_cls = self.registry.get_module_class(module_name)
            if module_cls is None:
                continue
            module_instance = module_cls()
            self.registry.activate(module_name, module_instance)
            result = module_instance.startup({"registry": self.registry, "event_bus": self.event_bus})
            if asyncio.iscoroutine(result):
                await result

    async def shutdown(self) -> None:
        for module_name in reversed(self.registry.list_modules()):
            module = self.registry.get_module(module_name)
            if module is None:
                continue
            result = module.shutdown({"registry": self.registry, "event_bus": self.event_bus})
            if asyncio.iscoroutine(result):
                await result

    def create(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self.startup()
            yield
            await self.shutdown()

        app = FastAPI(title="SOFIA", lifespan=lifespan)
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

        self._register_routes(app)

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
                "zabbix": self.settings.ZABBIX_URL,
            }

        app.state.sofia_core = self
        return app

    def _register_routes(self, app: FastAPI) -> None:
        from routes.ai import router as ai_router
        from routes.assistant import router as assistant_router
        from routes.context import router as context_router
        from routes.core import router as core_router
        from routes.docs import router as docs_router
        from routes.engine import router as engine_router
        from routes.health import router as health_router
        from routes.infra import router as infra_router
        from routes.knowledge import router as knowledge_router
        from routes.learning import router as learning_router
        from routes.marketplace import router as marketplace_router
        from routes.mcp import router as mcp_router
        from routes.security import router as security_router
        from routes.workflows import router as workflows_router
        from routes.zabbix import router as zabbix_router

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
