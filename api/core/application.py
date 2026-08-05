from __future__ import annotations

import asyncio
import hmac
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from services.auth import auth_service
from services.automation_graph import automation_graph_store
from fastapi.staticfiles import StaticFiles
import pyotp

from config.settings import settings
from core.autonomy_scheduler import AutonomyScheduler
from core.bootstrap import bootstrap_registry
from core.event_bus import event_bus
from core.event_handlers import register_default_event_handlers
from core.registry import registry
from core.snapshot_scheduler import SnapshotScheduler


class Application:
    def __init__(self):
        self.settings = settings
        self.registry = registry
        self.event_bus = event_bus
        self.snapshot_scheduler = SnapshotScheduler(interval_seconds=self.settings.SNAPSHOT_INTERVAL_SECONDS)
        self.autonomy_scheduler = AutonomyScheduler(
            interval_seconds=self.settings.AUTONOMOUS_INVESTIGATION_INTERVAL_SECONDS
        )
        self._request_buckets: dict[str, deque[float]] = defaultdict(deque)

    async def startup(self) -> None:
        # Kernel dependencies are registered once and reused via registry.get(...).
        self.registry.clear()
        self.event_bus.clear()

        snapshot = bootstrap_registry()
        self.registry.register_service("settings", self.settings)
        self.registry.register_service("event_bus", self.event_bus)
        self.registry.register_service("registry_snapshot", snapshot)
        register_default_event_handlers(self.event_bus)
        self.registry.register_service("snapshot_scheduler", self.snapshot_scheduler)
        self.registry.register_service("autonomy_scheduler", self.autonomy_scheduler)

        for module_name in self.registry.list_modules():
            module_cls = self.registry.get_module_class(module_name)
            if module_cls is None:
                continue
            module_instance = module_cls()
            self.registry.activate(module_name, module_instance)
            result = module_instance.startup({"registry": self.registry, "event_bus": self.event_bus})
            if asyncio.iscoroutine(result):
                await result

        auth_service.ensure_schema()
        automation_graph_store.ensure_schema()
        await self.snapshot_scheduler.start()
        await self.autonomy_scheduler.start()

    async def shutdown(self) -> None:
        await self.autonomy_scheduler.stop()
        await self.snapshot_scheduler.stop()
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
            protected_write_paths = {
                "/marketplace/install",
                "/workflows/run",
                "/workflows/n8n/run",
                "/engine/ingest",
                "/knowledge/providers",
                "/knowledge/providers/refresh",
                "/knowledge/upload",
                "/knowledge/ingest",
                "/knowledge/ingest/site",
                "/zabbix/groups",
            }
            path = request.url.path
            method = request.method.upper()
            public_paths = {"/", "/login.html", "/health", "/mcp/health", "/security/validate", "/auth/login", "/auth/first-access/start", "/auth/first-access/complete", "/auth/access-requests"}
            is_static = path.startswith("/ui/")
            if path not in public_paths and not is_static:
                authorization = request.headers.get("authorization", "")
                token = authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
                user = auth_service.authenticate(token)
                if not user:
                    return JSONResponse(status_code=401, content={"detail": "sessão inválida ou expirada"})
                request.state.user = user
                admin_prefixes = ("/knowledge", "/marketplace", "/workflows", "/engine", "/learning", "/zabbix", "/infra", "/core", "/docs")
                if user["role"] != "admin" and path.startswith(admin_prefixes):
                    return JSONResponse(status_code=403, content={"detail": "perfil admin necessário"})

            # Enforce admin API key and optional TOTP for critical mutating endpoints.
            if method in {"POST", "PUT", "PATCH", "DELETE"} and path in protected_write_paths and not (getattr(request.state, "user", None) and request.state.user.get("role") == "admin"):
                expected_key = self.settings.SECURITY_ADMIN_API_KEY.strip()
                if expected_key:
                    received_key = request.headers.get("x-sofia-admin-key", "").strip()
                    if not received_key or not hmac.compare_digest(received_key, expected_key):
                        return JSONResponse(status_code=401, content={"detail": "admin api key required"})

                    mfa_secret = self.settings.SECURITY_MFA_TOTP_SECRET.strip()
                    if mfa_secret:
                        otp = request.headers.get("x-sofia-otp", "").strip()
                        if not otp or not pyotp.TOTP(mfa_secret).verify(otp, valid_window=1):
                            return JSONResponse(status_code=401, content={"detail": "valid TOTP required"})

            content_length = int(request.headers.get("content-length", "0") or 0)
            if content_length > 25 * 1024 * 1024:
                return JSONResponse(status_code=413, content={"detail": "request body too large"})

            # Rate limit AI and authentication endpoints independently.
            if path in {"/assistant/ask", "/ai/ask", "/auth/login", "/auth/first-access/start", "/auth/first-access/complete", "/auth/access-requests"}:
                limit = 10 if path.startswith("/auth/") else max(10, int(self.settings.REQUEST_RATE_LIMIT_PER_MINUTE))
                client_ip = request.client.host if request.client and request.client.host else "unknown"
                key = f"{client_ip}:{path}"
                now = time.time()
                bucket = self._request_buckets[key]
                while bucket and now - bucket[0] > 60:
                    bucket.popleft()
                if len(bucket) >= limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "rate limit exceeded", "limit_per_minute": limit},
                    )
                bucket.append(now)

            response = await call_next(request)
            if path.startswith("/ui/") or path.startswith("/auth/") or path == "/login.html":
                response.headers["Cache-Control"] = "no-store"
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            return response

        self._register_routes(app)

        @app.get("/", include_in_schema=False)
        def home():
            return RedirectResponse(url="/login.html", status_code=302)

        @app.get("/login.html", include_in_schema=False)
        def login_page():
            return FileResponse("static/login.html", headers={"Cache-Control": "no-store"})

        app.state.sofia_core = self
        return app

    def _register_routes(self, app: FastAPI) -> None:
        from routes.auth import router as auth_router
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
        app.include_router(auth_router)
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
