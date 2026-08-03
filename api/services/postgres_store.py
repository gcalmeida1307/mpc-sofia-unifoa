from __future__ import annotations

from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from config.settings import settings


class PostgresStore:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or settings.POSTGRES_DSN
        self._ready = False

    def _connect(self):
        return psycopg.connect(self.dsn)

    def ensure_schema(self) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS assistant_messages (
                            id BIGSERIAL PRIMARY KEY,
                            role TEXT NOT NULL,
                            text TEXT NOT NULL,
                            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS assistant_insights (
                            id BIGSERIAL PRIMARY KEY,
                            signature TEXT NOT NULL UNIQUE,
                            kind TEXT NOT NULL,
                            summary TEXT NOT NULL,
                            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                conn.commit()
            self._ready = True
            return True
        except Exception:
            self._ready = False
            return False

    def add_message(self, role: str, text: str, metadata: dict[str, Any] | None = None) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO assistant_messages (role, text, metadata) VALUES (%s, %s, %s)",
                        (role, text, Jsonb(metadata or {})),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_recent_messages(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT role, text, metadata, created_at
                        FROM assistant_messages
                        ORDER BY id DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            rows.reverse()
            return [
                {
                    "role": role,
                    "text": text,
                    "metadata": metadata,
                    "created_at": created_at.isoformat() if created_at else None,
                }
                for role, text, metadata, created_at in rows
            ]
        except Exception:
            return []

    def save_insight(self, signature: str, kind: str, summary: str, payload: dict[str, Any] | None = None) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO assistant_insights (signature, kind, summary, payload, updated_at)
                        VALUES (%s, %s, %s, %s, NOW())
                        ON CONFLICT (signature)
                        DO UPDATE SET
                            kind = EXCLUDED.kind,
                            summary = EXCLUDED.summary,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        """,
                        (signature, kind, summary, Jsonb(payload or {})),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_recent_insights(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT signature, kind, summary, payload, created_at, updated_at
                        FROM assistant_insights
                        ORDER BY updated_at DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            return [
                {
                    "signature": signature,
                    "kind": kind,
                    "summary": summary,
                    "payload": payload,
                    "created_at": created_at.isoformat() if created_at else None,
                    "updated_at": updated_at.isoformat() if updated_at else None,
                }
                for signature, kind, summary, payload, created_at, updated_at in rows
            ]
        except Exception:
            return []


postgres_store = PostgresStore()