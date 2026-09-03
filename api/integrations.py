"""Isolated institutional ingestion layer for TASY and future connectors.

This module only reads configured systems. It does not create synthetic records,
does not put raw payloads in application logs, and keeps synchronization state
separate from the document RAG database.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "integrations.sqlite3"
MAX_PAGE_SIZE = 200


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _database() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize() -> None:
    """Create the local job ledger without creating any business data."""
    with _database() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS integration_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connector TEXT NOT NULL,
                resource TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                next_cursor TEXT,
                inserted_count INTEGER NOT NULL DEFAULT 0,
                changed_count INTEGER NOT NULL DEFAULT 0,
                unchanged_count INTEGER NOT NULL DEFAULT 0,
                error TEXT
            );
            CREATE TABLE IF NOT EXISTS integration_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connector TEXT NOT NULL,
                resource TEXT NOT NULL,
                external_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                first_received_at TEXT NOT NULL,
                last_received_at TEXT NOT NULL,
                UNIQUE (connector, resource, external_id)
            );
            CREATE TABLE IF NOT EXISTS integration_checkpoints (
                connector TEXT NOT NULL,
                resource TEXT NOT NULL,
                cursor TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (connector, resource)
            );
            CREATE TABLE IF NOT EXISTS integration_dlq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                connector TEXT NOT NULL,
                resource TEXT NOT NULL,
                payload_json TEXT,
                error TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES integration_jobs(id)
            );
            """
        )


@dataclass(frozen=True)
class Page:
    records: list[dict[str, Any]]
    next_cursor: str | None


class TasyConnector:
    """Small cursor-based HTTP adapter; the hospital-specific mapping stays configurable."""

    name = "tasy"

    @property
    def base_url(self) -> str:
        return os.getenv("SOFIA_TASY_BASE_URL", "").strip().rstrip("/")

    @property
    def token(self) -> str:
        return os.getenv("SOFIA_TASY_TOKEN", "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.token)

    def fetch_page(self, resource: str, cursor: str | None) -> Page:
        if not self.configured:
            raise RuntimeError("TASY não configurado: defina SOFIA_TASY_BASE_URL e SOFIA_TASY_TOKEN")
        safe_resource = "/" + re.sub(r"[^a-zA-Z0-9_./-]", "", resource).strip("/")
        if safe_resource == "/":
            raise ValueError("resource do TASY não pode ser vazio")
        try:
            timeout = max(2.0, min(60.0, float(os.getenv("SOFIA_TASY_TIMEOUT_SECONDS", "15"))))
        except ValueError:
            timeout = 15.0
        params: dict[str, str | int] = {"limit": min(MAX_PAGE_SIZE, max(1, int(os.getenv("SOFIA_TASY_PAGE_SIZE", "100"))))}
        if cursor:
            params["cursor"] = cursor
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        with httpx.Client(base_url=self.base_url, timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = client.get(safe_resource, params=params)
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            return Page([item for item in payload if isinstance(item, dict)], None)
        if not isinstance(payload, dict):
            raise TypeError("A resposta do TASY não é um objeto ou uma lista JSON")
        records_value = payload.get("data", payload.get("items", payload.get("results", payload.get("records", payload.get("entry", [])))))
        records = records_value if isinstance(records_value, list) else []
        next_cursor = payload.get("next_cursor", payload.get("nextCursor", payload.get("next")))
        return Page([item for item in records if isinstance(item, dict)], str(next_cursor) if next_cursor else None)


CONNECTORS = {"tasy": TasyConnector()}


def _external_id(record: dict[str, Any]) -> str:
    for key in ("id", "uuid", "external_id", "externalId", "code", "codigo"):
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return hashlib.sha256(_canonical(record).encode()).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _upsert_raw(connection: sqlite3.Connection, connector: str, resource: str, record: dict[str, Any], received_at: str) -> str:
    external_id = _external_id(record)
    payload_json = _canonical(record)
    payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
    existing = connection.execute(
        "SELECT payload_hash FROM integration_raw WHERE connector = ? AND resource = ? AND external_id = ?",
        (connector, resource, external_id),
    ).fetchone()
    if existing is None:
        connection.execute(
            "INSERT INTO integration_raw (connector, resource, external_id, payload_json, payload_hash, first_received_at, last_received_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (connector, resource, external_id, payload_json, payload_hash, received_at, received_at),
        )
        return "inserted"
    if existing["payload_hash"] == payload_hash:
        connection.execute(
            "UPDATE integration_raw SET last_received_at = ? WHERE connector = ? AND resource = ? AND external_id = ?",
            (received_at, connector, resource, external_id),
        )
        return "unchanged"
    connection.execute(
        "UPDATE integration_raw SET payload_json = ?, payload_hash = ?, last_received_at = ? WHERE connector = ? AND resource = ? AND external_id = ?",
        (payload_json, payload_hash, received_at, connector, resource, external_id),
    )
    return "changed"


def _checkpoint(connection: sqlite3.Connection, connector: str, resource: str, cursor: str | None) -> None:
    connection.execute(
        "INSERT INTO integration_checkpoints (connector, resource, cursor, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(connector, resource) DO UPDATE SET cursor = excluded.cursor, updated_at = excluded.updated_at",
        (connector, resource, cursor, _now()),
    )


def sync(connector_name: str = "tasy", resource: str = "patients", max_pages: int = 1) -> dict[str, Any]:
    """Run a bounded, resumable read and return counts only, never raw payloads."""
    if connector_name not in CONNECTORS:
        raise ValueError(f"Conector desconhecido: {connector_name}")
    if not 1 <= max_pages <= 20:
        raise ValueError("max_pages deve estar entre 1 e 20")
    connector = CONNECTORS[connector_name]
    initialize()
    started_at = _now()
    with _database() as connection:
        job = connection.execute(
            "INSERT INTO integration_jobs (connector, resource, status, started_at) VALUES (?, ?, 'running', ?)",
            (connector_name, resource, started_at),
        )
        job_id = int(job.lastrowid)
        checkpoint = connection.execute(
            "SELECT cursor FROM integration_checkpoints WHERE connector = ? AND resource = ?",
            (connector_name, resource),
        ).fetchone()
        cursor = checkpoint["cursor"] if checkpoint else None
        counts = {"inserted": 0, "changed": 0, "unchanged": 0, "dlq": 0}
        try:
            for _ in range(max_pages):
                page = connector.fetch_page(resource, cursor)
                for record in page.records:
                    try:
                        outcome = _upsert_raw(connection, connector_name, resource, record, _now())
                        counts[outcome] += 1
                    except Exception as exc:  # noqa: BLE001
                        connection.execute(
                            "INSERT INTO integration_dlq (job_id, connector, resource, payload_json, error, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (job_id, connector_name, resource, _canonical(record), str(exc), _now()),
                        )
                        counts["dlq"] += 1
                cursor = page.next_cursor
                _checkpoint(connection, connector_name, resource, cursor)
                if not page.records or not cursor:
                    break
            status = "completed_with_errors" if counts["dlq"] else "completed"
            connection.execute(
                "UPDATE integration_jobs SET status = ?, finished_at = ?, next_cursor = ?, inserted_count = ?, changed_count = ?, unchanged_count = ? WHERE id = ?",
                (status, _now(), cursor, counts["inserted"], counts["changed"], counts["unchanged"], job_id),
            )
            return {"job_id": job_id, "connector": connector_name, "resource": resource, "status": status, "next_cursor": cursor, "counts": counts}
        except Exception as exc:
            connection.execute(
                "INSERT INTO integration_dlq (job_id, connector, resource, payload_json, error, created_at) VALUES (?, ?, ?, NULL, ?, ?)",
                (job_id, connector_name, resource, str(exc), _now()),
            )
            connection.execute("UPDATE integration_jobs SET status = 'failed', finished_at = ?, error = ? WHERE id = ?", (_now(), str(exc), job_id))
            raise RuntimeError(f"Sincronização {connector_name}/{resource} falhou: {exc}") from exc


def status() -> dict[str, Any]:
    initialize()
    connector = CONNECTORS["tasy"]
    with _database() as connection:
        jobs = connection.execute("SELECT COUNT(*) AS total, SUM(status = 'running') AS running, SUM(status = 'failed') AS failed FROM integration_jobs").fetchone()
        last_job = connection.execute("SELECT id, connector, resource, status, started_at, finished_at, inserted_count, changed_count, unchanged_count, error FROM integration_jobs ORDER BY id DESC LIMIT 1").fetchone()
        dlq_pending = connection.execute("SELECT COUNT(*) AS count FROM integration_dlq WHERE status = 'pending'").fetchone()["count"]
    return {
        "storage": str(DATABASE_PATH),
        "mode": "local_raw_audit",
        "connectors": {
            "tasy": {
                "name": "TASY",
                "configured": connector.configured,
                "status": "ready" if connector.configured else "not_configured",
                "base_url": connector.base_url or None,
                "transport": "HTTP JSON paginado",
            },
            "protheus": {"name": "Protheus", "configured": False, "status": "planned"},
            "lyceum": {"name": "Lyceum", "configured": False, "status": "planned"},
            "fluig": {"name": "Fluig", "configured": False, "status": "planned"},
        },
        "jobs": {"total": int(jobs["total"] or 0), "running": int(jobs["running"] or 0), "failed": int(jobs["failed"] or 0)},
        "dlq_pending": int(dlq_pending),
        "last_job": dict(last_job) if last_job else None,
        "guarantees": ["RAW preservado localmente", "checkpoint por conector e recurso", "detecção novo/alterado/inalterado", "DLQ para falhas persistentes", "payload não aparece em logs de aplicação"],
    }


__all__ = ["initialize", "status", "sync"]
