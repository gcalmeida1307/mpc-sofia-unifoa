from __future__ import annotations

from typing import Any
from uuid import uuid4

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
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS infra_snapshots (
                            id BIGSERIAL PRIMARY KEY,
                            generated_at TIMESTAMPTZ NOT NULL,
                            summary JSONB NOT NULL DEFAULT '{}'::jsonb,
                            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS tool_execution_audit (
                            id BIGSERIAL PRIMARY KEY,
                            trace_id TEXT NOT NULL,
                            tool TEXT NOT NULL,
                            success BOOLEAN NOT NULL,
                            duration DOUBLE PRECISION NOT NULL DEFAULT 0,
                            evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
                            rollback_hint TEXT NULL,
                            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS ai_response_metrics (
                            id BIGSERIAL PRIMARY KEY,
                            question TEXT NOT NULL,
                            intent TEXT NOT NULL,
                            llm_used BOOLEAN NOT NULL,
                            latency_ms INTEGER NOT NULL DEFAULT 0,
                            confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
                            critic_approved BOOLEAN NOT NULL DEFAULT FALSE,
                            tokens_in INTEGER NOT NULL DEFAULT 0,
                            tokens_out INTEGER NOT NULL DEFAULT 0,
                            cost_usd DOUBLE PRECISION NOT NULL DEFAULT 0,
                            tools JSONB NOT NULL DEFAULT '[]'::jsonb,
                            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
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

    def save_snapshot(self, snapshot: dict[str, Any], summary: dict[str, Any]) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            generated_at = snapshot.get("generated_at")
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO infra_snapshots (generated_at, summary, payload)
                        VALUES (COALESCE(%s::timestamptz, NOW()), %s, %s)
                        """,
                        (generated_at, Jsonb(summary or {}), Jsonb(snapshot or {})),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_recent_snapshots(self, limit: int = 30) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT generated_at, summary, payload
                        FROM infra_snapshots
                        ORDER BY generated_at DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            return [
                {
                    "generated_at": generated_at.isoformat() if generated_at else None,
                    "summary": summary,
                    "payload": payload,
                }
                for generated_at, summary, payload in rows
            ]
        except Exception:
            return []

    def get_group_trends(self, days: int = 30, limit: int = 10) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            group_name,
                            COUNT(*)::int AS occurrences,
                            COUNT(DISTINCT host_name)::int AS unique_hosts
                        FROM (
                            SELECT
                                trim(both '"' from grp.group_name) AS group_name,
                                trim(both '"' from COALESCE(hst.host_name, '')) AS host_name
                            FROM infra_snapshots snap
                            CROSS JOIN LATERAL jsonb_array_elements(COALESCE(snap.payload->'zabbix'->'problems', '[]'::jsonb)) AS problem
                            LEFT JOIN LATERAL jsonb_array_elements_text(COALESCE(problem->'groups', '[]'::jsonb)) AS grp(group_name) ON TRUE
                            LEFT JOIN LATERAL jsonb_array_elements_text(COALESCE(problem->'hosts', '[]'::jsonb)) AS hst(host_name) ON TRUE
                            WHERE snap.generated_at >= NOW() - (%s || ' days')::interval
                        ) normalized
                        WHERE group_name <> ''
                        GROUP BY group_name
                        ORDER BY occurrences DESC
                        LIMIT %s
                        """,
                        (str(days), limit),
                    )
                    rows = cur.fetchall()
            return [
                {
                    "group": group,
                    "occurrences": occurrences,
                    "unique_hosts": unique_hosts,
                }
                for group, occurrences, unique_hosts in rows
            ]
        except Exception:
            return []

    def save_tool_audit(self, traces: list[dict[str, Any]], metadata: dict[str, Any] | None = None) -> bool:
        if not traces:
            return True
        if not self._ready and not self.ensure_schema():
            return False
        trace_id = str(uuid4())
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    for trace in traces:
                        cur.execute(
                            """
                            INSERT INTO tool_execution_audit (trace_id, tool, success, duration, evidence, rollback_hint, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                trace_id,
                                trace.get("tool", ""),
                                bool(trace.get("success", False)),
                                float(trace.get("duration", 0.0) or 0.0),
                                Jsonb(trace.get("evidence", [])),
                                trace.get("rollback"),
                                Jsonb(metadata or {}),
                            ),
                        )
                conn.commit()
            return True
        except Exception:
            return False

    def get_recent_tool_audits(self, limit: int = 100) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT trace_id, tool, success, duration, evidence, rollback_hint, metadata, created_at
                        FROM tool_execution_audit
                        ORDER BY id DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            return [
                {
                    "trace_id": trace_id,
                    "tool": tool,
                    "success": success,
                    "duration": duration,
                    "evidence": evidence,
                    "rollback_hint": rollback_hint,
                    "metadata": metadata,
                    "created_at": created_at.isoformat() if created_at else None,
                }
                for trace_id, tool, success, duration, evidence, rollback_hint, metadata, created_at in rows
            ]
        except Exception:
            return []

    def save_ai_metric(
        self,
        *,
        question: str,
        intent: str,
        llm_used: bool,
        latency_ms: int,
        confidence: float,
        critic_approved: bool,
        tokens_in: int,
        tokens_out: int,
        cost_usd: float,
        tools: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO ai_response_metrics (
                            question, intent, llm_used, latency_ms, confidence, critic_approved,
                            tokens_in, tokens_out, cost_usd, tools, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            question,
                            intent,
                            llm_used,
                            latency_ms,
                            confidence,
                            critic_approved,
                            tokens_in,
                            tokens_out,
                            cost_usd,
                            Jsonb(tools),
                            Jsonb(metadata or {}),
                        ),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_ai_metrics_summary(self, hours: int = 24) -> dict[str, Any]:
        if not self._ready and not self.ensure_schema():
            return {
                "window_hours": hours,
                "total_questions": 0,
                "avg_latency_ms": 0,
                "avg_confidence": 0,
                "llm_usage_rate": 0,
                "critic_approval_rate": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "estimated_cost_usd": 0,
                "top_tools": [],
            }

        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            COUNT(*)::int,
                            COALESCE(AVG(latency_ms), 0)::float,
                            COALESCE(AVG(confidence), 0)::float,
                            COALESCE(AVG(CASE WHEN llm_used THEN 1 ELSE 0 END), 0)::float,
                            COALESCE(AVG(CASE WHEN critic_approved THEN 1 ELSE 0 END), 0)::float,
                            COALESCE(SUM(tokens_in), 0)::int,
                            COALESCE(SUM(tokens_out), 0)::int,
                            COALESCE(SUM(cost_usd), 0)::float
                        FROM ai_response_metrics
                        WHERE created_at >= NOW() - (%s || ' hours')::interval
                        """,
                        (str(hours),),
                    )
                    totals = cur.fetchone()

                    cur.execute(
                        """
                        SELECT tool, COUNT(*)::int AS uses
                        FROM ai_response_metrics,
                             jsonb_array_elements_text(tools) AS tool
                        WHERE created_at >= NOW() - (%s || ' hours')::interval
                        GROUP BY tool
                        ORDER BY uses DESC
                        LIMIT 10
                        """,
                        (str(hours),),
                    )
                    top_tools = [{"tool": tool, "uses": uses} for tool, uses in cur.fetchall()]

            return {
                "window_hours": hours,
                "total_questions": totals[0],
                "avg_latency_ms": round(totals[1], 2),
                "avg_confidence": round(totals[2], 3),
                "llm_usage_rate": round(totals[3], 3),
                "critic_approval_rate": round(totals[4], 3),
                "total_tokens_in": totals[5],
                "total_tokens_out": totals[6],
                "estimated_cost_usd": round(totals[7], 6),
                "top_tools": top_tools,
            }
        except Exception:
            return {
                "window_hours": hours,
                "total_questions": 0,
                "avg_latency_ms": 0,
                "avg_confidence": 0,
                "llm_usage_rate": 0,
                "critic_approval_rate": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "estimated_cost_usd": 0,
                "top_tools": [],
            }


postgres_store = PostgresStore()