"""Runtime storage policy shared by all operational subsystems."""

from __future__ import annotations

import os
from typing import Any

try:
    import psycopg
except ImportError:  # pragma: no cover - optional in local developer mode
    psycopg = None


def postgres_dsn() -> str:
    return os.getenv("SOFIA_POSTGRES_URL", os.getenv("DATABASE_URL", "")).strip()


def strict_storage() -> bool:
    mode = os.getenv("SOFIA_STORAGE_MODE", "developer").strip().casefold()
    return mode in {"production", "strict", "primary"}


def status() -> dict[str, Any]:
    dsn = postgres_dsn()
    result: dict[str, Any] = {
        "mode": "production-primary" if strict_storage() else "developer-fallback-allowed",
        "postgres_configured": bool(dsn),
        "driver_available": psycopg is not None,
        "backend": "postgresql" if dsn and psycopg is not None else "sqlite",
        "healthy": False,
        "error": None,
        "postgresql_scope": ["knowledge_pipeline", "analytics", "observability"],
        "local_scope_pending_migration": ["auth", "fhir", "integrations", "insights"],
    }
    if not dsn:
        result["error"] = "SOFIA_POSTGRES_URL/DATABASE_URL não configurada"
        return result
    if psycopg is None:
        result["error"] = "psycopg não está instalado"
        return result
    try:
        with psycopg.connect(dsn, connect_timeout=3) as connection:
            connection.execute("SELECT 1")
        result["healthy"] = True
    except Exception as exc:  # noqa: BLE001
        result["backend"] = "sqlite-fallback"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
    return result


def assert_primary_ready() -> dict[str, Any]:
    current = status()
    if strict_storage() and not current["healthy"]:
        raise RuntimeError(f"Armazenamento primário PostgreSQL indisponível: {current['error']}")
    return current
