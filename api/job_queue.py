"""Persistent, bounded job queue used by background SOFIA work.

SQLite is the local default. When the normal PostgreSQL connection is
configured, the same contract uses the PostgreSQL runtime schema. Payloads
are operational metadata only; document contents and user prompts do not
belong in this queue.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .pg_runtime import is_postgres, postgres_connection


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class Job:
    job_id: str
    job_type: str
    module_id: str
    payload: dict[str, Any]
    status: str
    attempts: int
    max_attempts: int
    available_at: str
    lease_until: str | None
    last_error: str | None


class PersistentJobQueue:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        configured = os.getenv("SOFIA_JOB_QUEUE_PATH", "").strip()
        self.path = Path(configured).expanduser() if configured else self.root.parent / "data" / "sofia-jobs.sqlite3"

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        with postgres_connection() as primary:
            if primary is not None:
                yield primary
                return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            if is_postgres(connection):
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sofia_jobs (
                        job_id TEXT PRIMARY KEY,
                        job_type TEXT NOT NULL,
                        module_id TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        status TEXT NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        max_attempts INTEGER NOT NULL DEFAULT 3,
                        available_at TEXT NOT NULL,
                        lease_until TEXT,
                        last_error TEXT,
                        idempotency_key TEXT UNIQUE,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
            else:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sofia_jobs (
                        job_id TEXT PRIMARY KEY,
                        job_type TEXT NOT NULL,
                        module_id TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        status TEXT NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0,
                        max_attempts INTEGER NOT NULL DEFAULT 3,
                        available_at TEXT NOT NULL,
                        lease_until TEXT,
                        last_error TEXT,
                        idempotency_key TEXT UNIQUE,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
            connection.commit()

    def enqueue(
        self,
        job_type: str,
        module_id: str,
        payload: dict[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
        max_attempts: int = 3,
    ) -> str:
        self.initialize()
        key = idempotency_key or f"{job_type}:{module_id}:{uuid.uuid4().hex}"
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT job_id FROM sofia_jobs WHERE idempotency_key = ?", (key,)
            ).fetchone()
            if existing:
                connection.commit()
                return str(existing[0])
            job_id = uuid.uuid4().hex
            now = _now()
            connection.execute(
                "INSERT INTO sofia_jobs (job_id, job_type, module_id, payload_json, status, attempts, max_attempts, available_at, lease_until, last_error, idempotency_key, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (job_id, job_type, module_id, json.dumps(payload or {}, ensure_ascii=False), "pending", 0, max(1, min(20, int(max_attempts))), now, None, None, key, now, now),
            )
            connection.commit()
            return job_id

    def _row(self, row: Any) -> Job:
        return Job(
            str(row["job_id"]),
            str(row["job_type"]),
            str(row["module_id"]),
            json.loads(str(row["payload_json"])),
            str(row["status"]),
            int(row["attempts"]),
            int(row["max_attempts"]),
            str(row["available_at"]),
            str(row["lease_until"]) if row["lease_until"] else None,
            str(row["last_error"]) if row["last_error"] else None,
        )

    def pending(self, job_type: str | None = None) -> list[Job]:
        self.initialize()
        with self._connection() as connection:
            if job_type:
                rows = connection.execute(
                    "SELECT * FROM sofia_jobs WHERE job_type = ? AND status IN ('pending', 'retry') ORDER BY created_at",
                    (job_type,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM sofia_jobs WHERE status IN ('pending', 'retry') ORDER BY created_at"
                ).fetchall()
        return [self._row(row) for row in rows]

    def claim(
        self,
        job_type: str,
        lease_seconds: int = 300,
        job_id: str | None = None,
    ) -> Job | None:
        self.initialize()
        now = datetime.now(UTC)
        now_text = now.isoformat()
        lease = (now + timedelta(seconds=max(5, min(86_400, lease_seconds)))).isoformat()
        with self._connection() as connection:
            if not is_postgres(connection):
                connection.execute("BEGIN IMMEDIATE")
            if job_id:
                row = connection.execute(
                    "SELECT * FROM sofia_jobs WHERE job_type = ? AND job_id = ? AND (status IN ('pending', 'retry') OR (status = 'running' AND lease_until < ?)) AND available_at <= ?",
                    (job_type, job_id, now_text, now_text),
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT * FROM sofia_jobs WHERE job_type = ? AND (status IN ('pending', 'retry') OR (status = 'running' AND lease_until < ?)) AND available_at <= ? ORDER BY created_at LIMIT 1",
                    (job_type, now_text, now_text),
                ).fetchone()
            if row is None:
                connection.commit()
                return None
            job_id = str(row["job_id"])
            connection.execute(
                "UPDATE sofia_jobs SET status = 'running', attempts = attempts + 1, lease_until = ?, updated_at = ? WHERE job_id = ?",
                (lease, now_text, job_id),
            )
            claimed = connection.execute("SELECT * FROM sofia_jobs WHERE job_id = ?", (job_id,)).fetchone()
            connection.commit()
        return self._row(claimed) if claimed else None

    def complete(self, job_id: str) -> bool:
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE sofia_jobs SET status = 'completed', lease_until = NULL, updated_at = ? WHERE job_id = ? AND status = 'running'",
                (_now(), job_id),
            )
            connection.commit()
            return cursor.rowcount > 0

    def fail(self, job_id: str, error: str, *, backoff_seconds: int = 30) -> Job | None:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM sofia_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if row is None:
                return None
            attempts = int(row["attempts"])
            max_attempts = int(row["max_attempts"])
            terminal = attempts >= max_attempts
            available = datetime.now(UTC) + timedelta(seconds=max(1, min(86_400, backoff_seconds * (2 ** max(0, attempts - 1)))))
            connection.execute(
                "UPDATE sofia_jobs SET status = ?, available_at = ?, lease_until = NULL, last_error = ?, updated_at = ? WHERE job_id = ?",
                ("dead" if terminal else "retry", available.isoformat(), str(error)[:1000], _now(), job_id),
            )
            updated = connection.execute("SELECT * FROM sofia_jobs WHERE job_id = ?", (job_id,)).fetchone()
            connection.commit()
        return self._row(updated) if updated else None

    def counts(self, job_type: str | None = None) -> dict[str, int]:
        self.initialize()
        with self._connection() as connection:
            if job_type:
                rows = connection.execute("SELECT status, COUNT(*) AS count FROM sofia_jobs WHERE job_type = ? GROUP BY status", (job_type,)).fetchall()
            else:
                rows = connection.execute("SELECT status, COUNT(*) AS count FROM sofia_jobs GROUP BY status").fetchall()
        return {str(row["status"]): int(row["count"]) for row in rows}


__all__ = ["Job", "PersistentJobQueue"]
