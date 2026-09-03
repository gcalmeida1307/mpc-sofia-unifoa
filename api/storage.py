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


_POSTGRES_SCOPE_TABLES: dict[str, set[tuple[str, str]]] = {
    "knowledge_pipeline": {
        ("sofia_runtime", "documents"),
        ("sofia_runtime", "document_chunks"),
        ("sofia_runtime", "knowledge_artifacts"),
        ("sofia_runtime", "processing_jobs"),
        ("sofia_runtime", "retrieval_tests"),
    },
    "auth": {
        ("sofia_runtime", "users"),
        ("sofia_runtime", "user_module_access"),
        ("sofia_runtime", "access_requests"),
        ("sofia_runtime", "sessions"),
        ("sofia_runtime", "account_activation_tokens"),
        ("sofia_runtime", "password_reset_tokens"),
    },
    "fhir": {("sofia_runtime", "fhir_resources")},
    "integrations": {
        ("sofia_runtime", "integration_jobs"),
        ("sofia_runtime", "integration_raw"),
        ("sofia_runtime", "integration_checkpoints"),
        ("sofia_runtime", "integration_dlq"),
    },
    "insights": {("sofia_runtime", "insights")},
    "analytics": {
        ("public", "sofia_query_analytics"),
        ("public", "sofia_learning_events"),
    },
    "observability": {
        ("public", "sofia_traces"),
        ("public", "sofia_trace_spans"),
    },
    "privacy_audit": {("sofia_runtime", "audit_events")},
}


def _postgres_scope(connection: Any) -> tuple[list[str], list[str], list[str]]:
    rows = connection.execute(
        "SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
    ).fetchall()
    available = {(str(row[0]), str(row[1])) for row in rows}
    ready: list[str] = []
    pending: list[str] = []
    missing_tables: list[str] = []
    for scope, required in _POSTGRES_SCOPE_TABLES.items():
        missing = sorted(f"{schema}.{table}" for schema, table in required - available)
        if missing:
            pending.append(scope)
            missing_tables.extend(missing)
        else:
            ready.append(scope)
    return sorted(ready), sorted(pending), missing_tables


def status() -> dict[str, Any]:
    dsn = postgres_dsn()
    result: dict[str, Any] = {
        "mode": "production-primary"
        if strict_storage()
        else "developer-fallback-allowed",
        "postgres_configured": bool(dsn),
        "driver_available": psycopg is not None,
        "backend": "postgresql" if dsn and psycopg is not None else "sqlite",
        "healthy": False,
        "error": None,
        "postgresql_scope": [],
        "local_scope_pending_migration": sorted(_POSTGRES_SCOPE_TABLES),
        "postgresql_missing_tables": [],
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
            ready, pending, missing_tables = _postgres_scope(connection)
        result["healthy"] = True
        result["postgresql_scope"] = ready
        result["local_scope_pending_migration"] = pending
        result["postgresql_missing_tables"] = missing_tables
    except Exception as exc:  # noqa: BLE001
        result["backend"] = "sqlite-fallback"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:240]}"
    return result


def assert_primary_ready() -> dict[str, Any]:
    current = status()
    if strict_storage() and not current["healthy"]:
        raise RuntimeError(
            f"Armazenamento primário PostgreSQL indisponível: {current['error']}"
        )
    return current
