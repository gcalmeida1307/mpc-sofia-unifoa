from __future__ import annotations

from typing import Any
from uuid import uuid4

import psycopg
from psycopg_pool import ConnectionPool
from psycopg.types.json import Jsonb

from config.settings import settings


class PostgresStore:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or settings.POSTGRES_DSN
        self._ready = False
        self._pool: ConnectionPool | None = None

    def _connect(self):
        if self._pool is None:
            self._pool = ConnectionPool(
                conninfo=self.dsn,
                min_size=settings.postgres.pool_min_size,
                max_size=settings.postgres.pool_max_size,
                open=False,
                name="sofia-platform",
            )
            self._pool.open(wait=True, timeout=5)
        return self._pool.connection(timeout=5)

    def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool = None
            self._ready = False

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
                        CREATE TABLE IF NOT EXISTS domain_snapshots (
                            id BIGSERIAL PRIMARY KEY,
                            domain_id TEXT NOT NULL,
                            generated_at TIMESTAMPTZ NOT NULL,
                            summary JSONB NOT NULL DEFAULT '{}'::jsonb,
                            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_domain_snapshots_identity ON domain_snapshots(domain_id, generated_at)")
                    cur.execute("""DO $$ BEGIN
                        IF to_regclass('public.infra_snapshots') IS NOT NULL THEN
                            INSERT INTO domain_snapshots(domain_id,generated_at,summary,payload,created_at)
                            SELECT 'infrastructure',generated_at,summary,payload,created_at FROM infra_snapshots
                            ON CONFLICT(domain_id,generated_at) DO NOTHING;
                        END IF;
                    END $$""")
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
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS ai_hypothesis_runs (
                            id BIGSERIAL PRIMARY KEY,
                            question TEXT NOT NULL,
                            symptom TEXT NOT NULL,
                            domain TEXT NOT NULL,
                            hypotheses JSONB NOT NULL DEFAULT '[]'::jsonb,
                            selected_hypothesis TEXT NULL,
                            confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
                            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS ai_learning_cycles (
                            id BIGSERIAL PRIMARY KEY,
                            question TEXT NOT NULL,
                            intent TEXT NOT NULL,
                            decision JSONB NOT NULL DEFAULT '{}'::jsonb,
                            evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
                            outcome JSONB NOT NULL DEFAULT '{}'::jsonb,
                            knowledge_updated BOOLEAN NOT NULL DEFAULT FALSE,
                            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS planner_policy_weights (
                            id BIGSERIAL PRIMARY KEY,
                            capability TEXT NOT NULL UNIQUE,
                            weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
                            success_count INTEGER NOT NULL DEFAULT 0,
                            failure_count INTEGER NOT NULL DEFAULT 0,
                            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS autonomous_investigations (
                            id BIGSERIAL PRIMARY KEY,
                            watcher TEXT NOT NULL,
                            title TEXT NOT NULL,
                            severity TEXT NOT NULL,
                            status TEXT NOT NULL DEFAULT 'open',
                            summary TEXT NOT NULL,
                            hypothesis JSONB NOT NULL DEFAULT '{}'::jsonb,
                            evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
                            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_assistant_messages_created_at ON assistant_messages(created_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_assistant_insights_kind_updated ON assistant_insights(kind, updated_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_domain_snapshots_lookup ON domain_snapshots(domain_id, generated_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_tool_audit_created_at ON tool_execution_audit(created_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_tool_audit_tool_status ON tool_execution_audit(tool, success, created_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_metrics_created_at ON ai_response_metrics(created_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_learning_cycles_created_at ON ai_learning_cycles(created_at DESC)")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_investigations_status_created ON autonomous_investigations(status, created_at DESC)")
                conn.commit()
            self._ready = True
            return True
        except Exception:
            self._ready = False
            return False

    def apply_retention(self, raw_snapshot_days: int = 30, audit_days: int = 90) -> dict[str, int]:
        """Delete only aged operational telemetry; user and knowledge records are never touched."""
        if not self._ready and not self.ensure_schema():
            return {"snapshots": 0, "tool_audits": 0, "ai_metrics": 0}
        limits = {"snapshots": max(7, raw_snapshot_days), "tool_audits": max(30, audit_days), "ai_metrics": max(30, audit_days)}
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM domain_snapshots WHERE generated_at < NOW() - (%s || ' days')::interval", (str(limits["snapshots"]),))
                    snapshots = cur.rowcount
                    cur.execute("DELETE FROM tool_execution_audit WHERE created_at < NOW() - (%s || ' days')::interval", (str(limits["tool_audits"]),))
                    audits = cur.rowcount
                    cur.execute("DELETE FROM ai_response_metrics WHERE created_at < NOW() - (%s || ' days')::interval", (str(limits["ai_metrics"]),))
                    metrics = cur.rowcount
                conn.commit()
            return {"snapshots": snapshots, "tool_audits": audits, "ai_metrics": metrics}
        except Exception:
            return {"snapshots": 0, "tool_audits": 0, "ai_metrics": 0}

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

    def save_snapshot(self, domain_id: str, snapshot: dict[str, Any], summary: dict[str, Any]) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            generated_at = snapshot.get("generated_at")
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO domain_snapshots (domain_id, generated_at, summary, payload)
                        VALUES (%s, COALESCE(%s::timestamptz, NOW()), %s, %s)
                        """,
                        (domain_id, generated_at, Jsonb(summary or {}), Jsonb(snapshot or {})),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_recent_snapshots(self, domain_id: str, limit: int = 30) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT generated_at, summary, payload
                        FROM domain_snapshots
                        WHERE domain_id = %s
                        ORDER BY generated_at DESC
                        LIMIT %s
                        """,
                        (domain_id, limit),
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
                            FROM domain_snapshots snap
                            CROSS JOIN LATERAL jsonb_array_elements(COALESCE(snap.payload->'zabbix'->'problems', '[]'::jsonb)) AS problem
                            LEFT JOIN LATERAL jsonb_array_elements_text(COALESCE(problem->'groups', '[]'::jsonb)) AS grp(group_name) ON TRUE
                            LEFT JOIN LATERAL jsonb_array_elements_text(COALESCE(problem->'hosts', '[]'::jsonb)) AS hst(host_name) ON TRUE
                            WHERE snap.domain_id = 'infrastructure' AND snap.generated_at >= NOW() - (%s || ' days')::interval
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

    def save_hypothesis_run(
        self,
        *,
        question: str,
        symptom: str,
        domain: str,
        hypotheses: list[dict[str, Any]],
        selected_hypothesis: str | None,
        confidence: float,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO ai_hypothesis_runs (
                            question, symptom, domain, hypotheses, selected_hypothesis, confidence, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            question,
                            symptom,
                            domain,
                            Jsonb(hypotheses),
                            selected_hypothesis,
                            confidence,
                            Jsonb(metadata or {}),
                        ),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_hypothesis_metrics_summary(self, hours: int = 24) -> dict[str, Any]:
        if not self._ready and not self.ensure_schema():
            return {
                "window_hours": hours,
                "total_runs": 0,
                "avg_confidence": 0,
                "confirmed_rate": 0,
                "top_domains": [],
            }
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            COUNT(*)::int,
                            COALESCE(AVG(confidence), 0)::float,
                            COALESCE(AVG(CASE WHEN COALESCE(metadata->>'confirmed', 'false') = 'true' THEN 1 ELSE 0 END), 0)::float
                        FROM ai_hypothesis_runs
                        WHERE created_at >= NOW() - (%s || ' hours')::interval
                        """,
                        (str(hours),),
                    )
                    totals = cur.fetchone()

                    cur.execute(
                        """
                        SELECT domain, COUNT(*)::int AS uses
                        FROM ai_hypothesis_runs
                        WHERE created_at >= NOW() - (%s || ' hours')::interval
                        GROUP BY domain
                        ORDER BY uses DESC
                        LIMIT 8
                        """,
                        (str(hours),),
                    )
                    top_domains = [{"domain": domain, "uses": uses} for domain, uses in cur.fetchall()]

            return {
                "window_hours": hours,
                "total_runs": totals[0],
                "avg_confidence": round(totals[1], 3),
                "confirmed_rate": round(totals[2], 3),
                "top_domains": top_domains,
            }
        except Exception:
            return {
                "window_hours": hours,
                "total_runs": 0,
                "avg_confidence": 0,
                "confirmed_rate": 0,
                "top_domains": [],
            }

    def save_learning_cycle(
        self,
        *,
        question: str,
        intent: str,
        decision: dict[str, Any],
        evidence: list[dict[str, Any]],
        outcome: dict[str, Any],
        knowledge_updated: bool,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO ai_learning_cycles (
                            question, intent, decision, evidence, outcome, knowledge_updated, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            question,
                            intent,
                            Jsonb(decision),
                            Jsonb(evidence),
                            Jsonb(outcome),
                            knowledge_updated,
                            Jsonb(metadata or {}),
                        ),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_learning_metrics_summary(self, hours: int = 24) -> dict[str, Any]:
        if not self._ready and not self.ensure_schema():
            return {
                "window_hours": hours,
                "total_cycles": 0,
                "knowledge_update_rate": 0,
                "reuse_rate": 0,
            }
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            COUNT(*)::int,
                            COALESCE(AVG(CASE WHEN knowledge_updated THEN 1 ELSE 0 END), 0)::float,
                            COALESCE(AVG(CASE WHEN COALESCE(metadata->>'reused', 'false') = 'true' THEN 1 ELSE 0 END), 0)::float
                        FROM ai_learning_cycles
                        WHERE created_at >= NOW() - (%s || ' hours')::interval
                        """,
                        (str(hours),),
                    )
                    totals = cur.fetchone()
            return {
                "window_hours": hours,
                "total_cycles": totals[0],
                "knowledge_update_rate": round(totals[1], 3),
                "reuse_rate": round(totals[2], 3),
            }
        except Exception:
            return {
                "window_hours": hours,
                "total_cycles": 0,
                "knowledge_update_rate": 0,
                "reuse_rate": 0,
            }

    def update_planner_policy(self, capability: str, success: bool, confidence_delta: float = 0.0) -> bool:
        if not capability:
            return False
        if not self._ready and not self.ensure_schema():
            return False
        try:
            weight_delta = 0.03 + max(-0.1, min(0.1, confidence_delta * 0.05))
            if not success:
                weight_delta = -weight_delta
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO planner_policy_weights (capability, weight, success_count, failure_count, updated_at)
                        VALUES (%s, %s, %s, %s, NOW())
                        ON CONFLICT (capability)
                        DO UPDATE SET
                            weight = LEAST(2.0, GREATEST(0.5, planner_policy_weights.weight + EXCLUDED.weight - 1.0)),
                            success_count = planner_policy_weights.success_count + EXCLUDED.success_count,
                            failure_count = planner_policy_weights.failure_count + EXCLUDED.failure_count,
                            updated_at = NOW()
                        """,
                        (capability, 1.0 + weight_delta, 1 if success else 0, 0 if success else 1),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_planner_policy_weights(self) -> dict[str, dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return {}
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT capability, weight, success_count, failure_count, updated_at
                        FROM planner_policy_weights
                        ORDER BY capability ASC
                        """
                    )
                    rows = cur.fetchall()
            return {
                capability: {
                    "weight": float(weight),
                    "success_count": int(success_count),
                    "failure_count": int(failure_count),
                    "updated_at": updated_at.isoformat() if updated_at else None,
                }
                for capability, weight, success_count, failure_count, updated_at in rows
            }
        except Exception:
            return {}

    def save_autonomous_investigation(
        self,
        *,
        watcher: str,
        title: str,
        severity: str,
        status: str,
        summary: str,
        hypothesis: dict[str, Any],
        evidence: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        if not self._ready and not self.ensure_schema():
            return False
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO autonomous_investigations (
                            watcher, title, severity, status, summary, hypothesis, evidence, metadata
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            watcher,
                            title,
                            severity,
                            status,
                            summary,
                            Jsonb(hypothesis),
                            Jsonb(evidence),
                            Jsonb(metadata or {}),
                        ),
                    )
                conn.commit()
            return True
        except Exception:
            return False

    def get_recent_autonomous_investigations(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self._ready and not self.ensure_schema():
            return []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT watcher, title, severity, status, summary, hypothesis, evidence, metadata, created_at
                        FROM autonomous_investigations
                        ORDER BY id DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cur.fetchall()
            return [
                {
                    "watcher": watcher,
                    "title": title,
                    "severity": severity,
                    "status": status,
                    "summary": summary,
                    "hypothesis": hypothesis,
                    "evidence": evidence,
                    "metadata": metadata,
                    "created_at": created_at.isoformat() if created_at else None,
                }
                for watcher, title, severity, status, summary, hypothesis, evidence, metadata, created_at in rows
            ]
        except Exception:
            return []

    def get_intelligence_metrics_summary(self, hours: int = 24) -> dict[str, Any]:
        ai_metrics = self.get_ai_metrics_summary(hours=hours)
        hypothesis_metrics = self.get_hypothesis_metrics_summary(hours=hours)
        learning_metrics = self.get_learning_metrics_summary(hours=hours)
        return {
            "window_hours": hours,
            "ai": ai_metrics,
            "hypothesis": hypothesis_metrics,
            "learning": learning_metrics,
        }


postgres_store = PostgresStore()
