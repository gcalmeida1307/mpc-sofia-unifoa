from __future__ import annotations

from typing import Any
from psycopg.types.json import Jsonb
from services.postgres_store import postgres_store


class LearningHistory:
    def ensure_schema(self) -> None:
        with postgres_store._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS learning_feedback (
                id BIGSERIAL PRIMARY KEY, domain_id TEXT NOT NULL, pattern_key TEXT NOT NULL,
                verdict TEXT NOT NULL CHECK(verdict IN ('confirmed','rejected')),
                evidence JSONB NOT NULL DEFAULT '{}'::jsonb, created_by BIGINT REFERENCES auth_users(id),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            conn.commit()

    def record(self, domain_id: str, pattern_key: str, verdict: str, evidence: dict[str, Any], user_id: int) -> dict[str, Any]:
        self.ensure_schema()
        with postgres_store._connect() as conn:
            row = conn.execute("INSERT INTO learning_feedback(domain_id,pattern_key,verdict,evidence,created_by) VALUES(%s,%s,%s,%s,%s) RETURNING id,created_at", (domain_id, pattern_key, verdict, Jsonb(evidence), user_id)).fetchone(); conn.commit()
        return {"id": row[0], "domain_id": domain_id, "pattern_key": pattern_key, "verdict": verdict, "evidence": evidence, "created_at": row[1].isoformat()}

    def status(self, domain_id: str, limit: int = 50) -> dict[str, Any]:
        self.ensure_schema()
        with postgres_store._connect() as conn:
            rows = conn.execute("SELECT pattern_key,verdict,evidence,created_at FROM learning_feedback WHERE domain_id=%s ORDER BY created_at DESC LIMIT %s", (domain_id, limit)).fetchall()
        confirmations = sum(1 for row in rows if row[1] == "confirmed")
        rejections = sum(1 for row in rows if row[1] == "rejected")
        return {"domain_id": domain_id, "baseline": {"feedback_samples": len(rows)}, "patterns": [{"pattern_key": r[0], "verdict": r[1], "evidence": r[2], "at": r[3].isoformat()} for r in rows], "confirmations": confirmations, "rejections": rejections, "changes": {"net_confirmations": confirmations - rejections}}


learning_history = LearningHistory()
