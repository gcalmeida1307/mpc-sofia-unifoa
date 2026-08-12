from __future__ import annotations

from typing import Any
from uuid import uuid4

from psycopg.types.json import Jsonb
from services.postgres_store import postgres_store


class InvestigationService:
    def ensure_schema(self) -> None:
        with postgres_store._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS investigations (
                investigation_id UUID PRIMARY KEY, domain_id TEXT NOT NULL, title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open', created_by BIGINT REFERENCES auth_users(id),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            conn.execute("""CREATE TABLE IF NOT EXISTS investigation_items (
                id BIGSERIAL PRIMARY KEY, investigation_id UUID NOT NULL REFERENCES investigations(investigation_id) ON DELETE CASCADE,
                item_type TEXT NOT NULL CHECK(item_type IN ('entity','event','hypothesis','evidence')),
                payload JSONB NOT NULL, verdict TEXT CHECK(verdict IN ('confirmed','rejected','pending')),
                created_by BIGINT REFERENCES auth_users(id), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            conn.commit()

    def create(self, domain_id: str, title: str, user_id: int) -> dict[str, Any]:
        self.ensure_schema(); investigation_id = str(uuid4())
        with postgres_store._connect() as conn:
            conn.execute("INSERT INTO investigations(investigation_id,domain_id,title,created_by) VALUES(%s,%s,%s,%s)", (investigation_id, domain_id, title, user_id)); conn.commit()
        return self.get(investigation_id)

    def add(self, investigation_id: str, item_type: str, payload: dict[str, Any], user_id: int, verdict: str | None = None) -> dict[str, Any]:
        self.ensure_schema()
        with postgres_store._connect() as conn:
            row = conn.execute("INSERT INTO investigation_items(investigation_id,item_type,payload,verdict,created_by) VALUES(%s,%s,%s,%s,%s) RETURNING id", (investigation_id, item_type, Jsonb(payload), verdict, user_id)).fetchone()
            conn.execute("UPDATE investigations SET updated_at=NOW() WHERE investigation_id=%s", (investigation_id,)); conn.commit()
        return {"id": row[0], "type": item_type, "payload": payload, "verdict": verdict}

    def get(self, investigation_id: str) -> dict[str, Any]:
        self.ensure_schema()
        with postgres_store._connect() as conn:
            row = conn.execute("SELECT investigation_id,domain_id,title,status,created_at,updated_at FROM investigations WHERE investigation_id=%s", (investigation_id,)).fetchone()
            if not row: raise KeyError(investigation_id)
            items = conn.execute("SELECT id,item_type,payload,verdict,created_at FROM investigation_items WHERE investigation_id=%s ORDER BY created_at", (investigation_id,)).fetchall()
        return {"investigation_id": str(row[0]), "domain_id": row[1], "title": row[2], "status": row[3], "created_at": row[4].isoformat(), "updated_at": row[5].isoformat(), "items": [{"id": i[0], "type": i[1], "payload": i[2], "verdict": i[3], "created_at": i[4].isoformat()} for i in items]}


investigation_service = InvestigationService()
