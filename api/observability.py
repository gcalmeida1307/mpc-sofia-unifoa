"""Privacy-safe trace store with PostgreSQL as production authority."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .storage import strict_storage

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - local fallback is intentional
    psycopg = None
    dict_row = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, user_code TEXT,
    module_id TEXT, intent TEXT, complexity TEXT, router TEXT, provider TEXT,
    model TEXT, status TEXT NOT NULL, confidence REAL, started_at TEXT NOT NULL,
    finished_at TEXT, latency_ms REAL, metrics_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS trace_spans (
    id INTEGER PRIMARY KEY AUTOINCREMENT, trace_id TEXT NOT NULL REFERENCES traces(trace_id),
    stage TEXT NOT NULL, status TEXT NOT NULL, started_at TEXT NOT NULL,
    finished_at TEXT, latency_ms REAL, metrics_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_traces_module_date ON traces(module_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_trace_spans_trace ON trace_spans(trace_id, id);
"""
PG_SCHEMA = """
CREATE TABLE IF NOT EXISTS sofia_traces (
    trace_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, user_code TEXT,
    module_id TEXT, intent TEXT, complexity TEXT, router TEXT, provider TEXT,
    model TEXT, status TEXT NOT NULL, confidence DOUBLE PRECISION,
    started_at TIMESTAMPTZ NOT NULL, finished_at TIMESTAMPTZ,
    latency_ms DOUBLE PRECISION, metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS sofia_trace_spans (
    id BIGSERIAL PRIMARY KEY, trace_id TEXT NOT NULL REFERENCES sofia_traces(trace_id) ON DELETE CASCADE,
    stage TEXT NOT NULL, status TEXT NOT NULL, started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ, latency_ms DOUBLE PRECISION, metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_sofia_traces_module_date ON sofia_traces(module_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sofia_trace_spans_trace ON sofia_trace_spans(trace_id, id);
"""


def database_path(root: Path) -> Path:
    return root.parent / "data" / "observability.sqlite3"


def _dsn() -> str:
    return os.getenv("SOFIA_POSTGRES_URL", os.getenv("DATABASE_URL", "")).strip()


def _postgres() -> Any | None:
    if not _dsn() or psycopg is None:
        return None
    try:
        return psycopg.connect(_dsn(), connect_timeout=5, row_factory=dict_row)
    except Exception as exc:
        if strict_storage():
            raise RuntimeError("PostgreSQL obrigatório indisponível para observabilidade") from exc
        return None


def _connect(root: Path) -> sqlite3.Connection:
    path = database_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.executescript(SCHEMA)
    return connection


def initialize(root: Path) -> None:
    connection = _postgres()
    if connection is not None:
        try:
            for statement in PG_SCHEMA.split(";"):
                if statement.strip():
                    connection.execute(statement)
            # Migrations can preserve explicit SQLite span ids.  Re-align the
            # PostgreSQL sequence before the next live trace appends a span.
            connection.execute(
                "SELECT setval(pg_get_serial_sequence('sofia_trace_spans', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM sofia_trace_spans"
            )
            connection.commit()
        finally:
            connection.close()
        return
    if strict_storage():
        raise RuntimeError("SOFIA_STORAGE_MODE exige PostgreSQL para observabilidade")
    connection = _connect(root)
    connection.commit()
    connection.close()


class TraceRecorder:
    def __init__(self, root: Path, module_id: str, question: str, user_code: str | None = None) -> None:
        self.root = root
        self.module_id = module_id
        self.user_code = user_code
        self.trace_id = uuid.uuid4().hex
        self.request_hash = hashlib.sha256(question.strip().casefold().encode()).hexdigest()
        self.started = time.perf_counter()
        connection = _postgres()
        if connection is not None:
            try:
                connection.execute("INSERT INTO sofia_traces (trace_id, request_hash, user_code, module_id, status, started_at) VALUES (%s, %s, %s, %s, 'RUNNING', %s)", (self.trace_id, self.request_hash, user_code, module_id, datetime.now(UTC)))
                connection.commit()
            finally:
                connection.close()
            return
        connection = _connect(root)
        connection.execute("INSERT INTO traces (trace_id, request_hash, user_code, module_id, status, started_at) VALUES (?, ?, ?, ?, 'RUNNING', ?)", (self.trace_id, self.request_hash, user_code, module_id, datetime.now(UTC).isoformat()))
        connection.commit()
        connection.close()

    def finish(self, *, status: str = "READY", intent: str | None = None, complexity: str | None = None, router: str | None = None, provider: str | None = None, model: str | None = None, confidence: float | None = None, metrics: dict[str, Any] | None = None) -> None:
        payload = json.dumps(metrics or {}, ensure_ascii=False)
        connection = _postgres()
        if connection is not None:
            try:
                connection.execute("UPDATE sofia_traces SET intent = %s, complexity = %s, router = %s, provider = %s, model = %s, status = %s, confidence = %s, finished_at = %s, latency_ms = %s, metrics_json = %s::jsonb WHERE trace_id = %s", (intent, complexity, router, provider, model, status, confidence, datetime.now(UTC), round((time.perf_counter() - self.started) * 1000, 2), payload, self.trace_id))
                connection.commit()
            finally:
                connection.close()
            return
        connection = _connect(self.root)
        connection.execute("UPDATE traces SET intent = ?, complexity = ?, router = ?, provider = ?, model = ?, status = ?, confidence = ?, finished_at = ?, latency_ms = ?, metrics_json = ? WHERE trace_id = ?", (intent, complexity, router, provider, model, status, confidence, datetime.now(UTC).isoformat(), round((time.perf_counter() - self.started) * 1000, 2), payload, self.trace_id))
        connection.commit()
        connection.close()

    def span(self, stage: str, status: str, metrics: dict[str, Any] | None = None, elapsed_ms: float | None = None) -> None:
        payload = json.dumps(metrics or {}, ensure_ascii=False)
        connection = _postgres()
        if connection is not None:
            try:
                connection.execute("INSERT INTO sofia_trace_spans (trace_id, stage, status, started_at, finished_at, latency_ms, metrics_json) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)", (self.trace_id, stage, status, datetime.now(UTC), datetime.now(UTC), elapsed_ms, payload))
                connection.commit()
            finally:
                connection.close()
            return
        connection = _connect(self.root)
        now = datetime.now(UTC).isoformat()
        connection.execute("INSERT INTO trace_spans (trace_id, stage, status, started_at, finished_at, latency_ms, metrics_json) VALUES (?, ?, ?, ?, ?, ?, ?)", (self.trace_id, stage, status, now, now, elapsed_ms, payload))
        connection.commit()
        connection.close()


def snapshot(root: Path, module_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    safe_limit = max(1, min(500, limit))
    connection = _postgres()
    if connection is not None:
        try:
            where = "WHERE module_id = %s" if module_id else ""
            args = (module_id, safe_limit) if module_id else (safe_limit,)
            rows = connection.execute(f"SELECT * FROM sofia_traces {where} ORDER BY started_at DESC LIMIT %s", args).fetchall()
            count_args = (module_id,) if module_id else ()
            count = connection.execute(f"SELECT COUNT(*) FROM sofia_traces {where}", count_args).fetchone()["count"]
            return {"database": "postgresql:sofia_traces", "backend": "postgresql", "total": int(count), "traces": [dict(row) for row in rows]}
        finally:
            connection.close()
    connection = _connect(root)
    try:
        where = "WHERE module_id = ?" if module_id else ""
        args = (module_id, safe_limit) if module_id else (safe_limit,)
        rows = connection.execute(f"SELECT * FROM traces {where} ORDER BY started_at DESC LIMIT ?", args).fetchall()
        count = connection.execute(f"SELECT COUNT(*) FROM traces {where}", (module_id,) if module_id else ()).fetchone()[0]
        return {"database": str(database_path(root)), "backend": "sqlite", "total": int(count), "traces": [dict(row) for row in rows]}
    finally:
        connection.close()
