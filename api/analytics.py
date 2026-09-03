from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .query_analysis import classify_query

logger = logging.getLogger("sofia.analytics")

try:
    import psycopg
except ImportError:  # The local SQLite adapter remains usable without PostgreSQL.
    psycopg = None

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS query_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    user_code TEXT,
    theme TEXT NOT NULL,
    intent TEXT NOT NULL,
    source_count INTEGER NOT NULL DEFAULT 0,
    provider TEXT NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    feedback TEXT,
    source_names TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
)
"""
POSTGRES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sofia_query_analytics (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    user_code TEXT,
    theme TEXT NOT NULL,
    intent TEXT NOT NULL,
    source_count INTEGER NOT NULL DEFAULT 0,
    provider TEXT NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    feedback TEXT,
    source_names TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL
)
"""
LEARNING_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS learning_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analytics_id INTEGER NOT NULL,
    module_id TEXT NOT NULL,
    theme TEXT NOT NULL,
    feedback TEXT NOT NULL,
    provider TEXT NOT NULL,
    source_names TEXT NOT NULL DEFAULT '',
    retry_requested INTEGER NOT NULL DEFAULT 0,
    training_scheduled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
)
"""
POSTGRES_LEARNING_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sofia_learning_events (
    id BIGSERIAL PRIMARY KEY,
    analytics_id BIGINT NOT NULL,
    module_id TEXT NOT NULL,
    theme TEXT NOT NULL,
    feedback TEXT NOT NULL,
    provider TEXT NOT NULL,
    source_names TEXT NOT NULL DEFAULT '',
    retry_requested BOOLEAN NOT NULL DEFAULT FALSE,
    training_scheduled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL
)
"""


def database_path(root: Path) -> Path:
    return root.parent / "data" / "agent_memory.sqlite3"


def _postgres_dsn() -> str:
    return os.getenv("SOFIA_POSTGRES_URL", os.getenv("DATABASE_URL", "")).strip()


def _storage(root: Path) -> str:
    return "postgresql" if _postgres_dsn() and psycopg is not None else "sqlite"


def _postgres_enabled() -> bool:
    return bool(_postgres_dsn() and psycopg is not None)


def initialize_analytics_store(root: Path) -> None:
    dsn = _postgres_dsn()
    if dsn and psycopg is not None:
        try:
            with psycopg.connect(dsn, connect_timeout=5) as connection:
                connection.execute(POSTGRES_TABLE_SQL)
                connection.execute("ALTER TABLE sofia_query_analytics ADD COLUMN IF NOT EXISTS feedback TEXT")
                connection.execute("ALTER TABLE sofia_query_analytics ADD COLUMN IF NOT EXISTS user_code TEXT")
                connection.execute("ALTER TABLE sofia_query_analytics ADD COLUMN IF NOT EXISTS source_names TEXT NOT NULL DEFAULT ''")
                connection.execute(POSTGRES_LEARNING_TABLE_SQL)
                connection.execute("CREATE INDEX IF NOT EXISTS idx_sofia_query_analytics_module_created ON sofia_query_analytics(module_id, created_at)")
                connection.execute("CREATE INDEX IF NOT EXISTS idx_sofia_query_analytics_theme ON sofia_query_analytics(module_id, theme)")
                connection.commit()
            return
        except Exception:
            # The local fallback keeps the browser usable while PostgreSQL is
            # being configured or temporarily unavailable.
            logger.debug("PostgreSQL analytics unavailable; using SQLite fallback", exc_info=True)
    path = database_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(TABLE_SQL)
        columns = {row[1] for row in connection.execute("PRAGMA table_info(query_analytics)").fetchall()}
        if "feedback" not in columns:
            connection.execute("ALTER TABLE query_analytics ADD COLUMN feedback TEXT")
        if "user_code" not in columns:
            connection.execute("ALTER TABLE query_analytics ADD COLUMN user_code TEXT")
        if "source_names" not in columns:
            connection.execute("ALTER TABLE query_analytics ADD COLUMN source_names TEXT NOT NULL DEFAULT ''")
        connection.execute(LEARNING_TABLE_SQL)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_query_analytics_module_created ON query_analytics(module_id, created_at)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_query_analytics_theme ON query_analytics(module_id, theme)")
        connection.commit()
    finally:
        connection.close()


def record_query(
    root: Path,
    module_id: str,
    question: str,
    sources: list[str],
    provider: str,
    verified: bool,
    feedback: str | None = None,
    user_code: str | None = None,
) -> int | None:
    """Persist only an explainable semantic label and operational metadata.

    The raw question and answer are intentionally absent from this table. The
    question is classified in memory and discarded after the insert.
    """
    profile = classify_query(module_id, question)
    dsn = _postgres_dsn()
    if dsn and psycopg is not None:
        try:
            with psycopg.connect(dsn, connect_timeout=5) as connection:
                row = connection.execute(
                    "INSERT INTO sofia_query_analytics (module_id, user_code, theme, intent, source_count, provider, verified, feedback, source_names, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (
                        module_id,
                        user_code,
                        str(profile["theme"]),
                        str(profile["intent"]),
                        len(sources),
                        provider,
                        verified,
                        feedback,
                        json.dumps(sources[:20], ensure_ascii=False),
                        datetime.now(UTC),
                    ),
                ).fetchone()
                connection.commit()
            return int(row[0]) if row else None
        except Exception:
            # Do not make an answer fail because the optional analytics DB is
            # offline. The local SQLite store is the development fallback.
            logger.debug("PostgreSQL analytics insert failed; using SQLite fallback", exc_info=True)
    initialize_analytics_store(root)
    connection = sqlite3.connect(database_path(root))
    try:
        row = connection.execute(
            "INSERT INTO query_analytics (module_id, user_code, theme, intent, source_count, provider, verified, feedback, source_names, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                module_id,
                user_code,
                str(profile["theme"]),
                str(profile["intent"]),
                len(sources),
                provider,
                int(verified),
                feedback,
                json.dumps(sources[:20], ensure_ascii=False),
                datetime.now(UTC).isoformat(),
            ),
        )
        connection.commit()
        return int(row.lastrowid)
    finally:
        connection.close()


def update_feedback(root: Path, analytics_id: int, feedback: str, user_code: str | None = None) -> bool:
    """Attach a non-sensitive quality signal to a previously returned answer."""
    if feedback not in {"good", "medium", "bad"}:
        raise ValueError("feedback deve ser good, medium ou bad")
    dsn = _postgres_dsn()
    if dsn and psycopg is not None:
        try:
            where = "id = %s"
            params: list[Any] = [analytics_id]
            if user_code:
                where += " AND (user_code = %s OR user_code IS NULL)"
                params.append(user_code)
            with psycopg.connect(dsn, connect_timeout=5) as connection:
                row = connection.execute(
                    f"UPDATE sofia_query_analytics SET feedback = %s WHERE {where} RETURNING id",
                    [feedback, *params],
                ).fetchone()
                connection.commit()
            if row:
                return True
        except Exception:
            logger.debug("PostgreSQL analytics feedback update failed; using SQLite fallback", exc_info=True)
    path = database_path(root)
    if not path.exists():
        return False
    initialize_analytics_store(root)
    connection = sqlite3.connect(path)
    try:
        where = "id = ?"
        params_sql: list[Any] = [analytics_id]
        if user_code:
            where += " AND (user_code = ? OR user_code IS NULL)"
            params_sql.append(user_code)
        cursor = connection.execute(f"UPDATE query_analytics SET feedback = ? WHERE {where}", [feedback, *params_sql])
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def _quality_summary(good: int, neutral: int, bad: int) -> dict[str, Any]:
    evaluated = good + bad
    return {
        "good_answers": good,
        "medium_answers": neutral,
        "bad_answers": bad,
        "evaluated_answers": evaluated,
        # Only explicit good/bad opinions are part of perceived quality.
        "quality_score": round(good / evaluated, 3) if evaluated else None,
        "needs_improvement": evaluated > 0 and bad > good,
    }


def _decode_sources(value: Any) -> list[str]:
    try:
        parsed = json.loads(str(value or "[]"))
    except (TypeError, ValueError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed[:20] if str(item).strip()]


def feedback_assessment(
    root: Path,
    analytics_id: int,
    user_code: str | None = None,
    days: int = 30,
) -> dict[str, Any] | None:
    """Return a privacy-preserving quality decision for one answer.

    The question and answer are deliberately never returned. The assessment
    contains only the module, semantic theme, sources and aggregate feedback
    needed to decide whether a retraining job should be queued.
    """
    safe_days = max(1, min(int(days), 365))
    dsn = _postgres_dsn()
    if dsn and psycopg is not None:
        try:
            since = datetime.now(UTC) - timedelta(days=safe_days)
            with psycopg.connect(dsn, connect_timeout=5) as connection:
                row = connection.execute(
                    "SELECT module_id, theme, provider, feedback, source_names FROM sofia_query_analytics WHERE id = %s AND (user_code = %s OR user_code IS NULL)",
                    (analytics_id, user_code),
                ).fetchone()
                if not row:
                    return None
                counts = connection.execute(
                    """
                    SELECT
                        COALESCE(SUM(CASE WHEN feedback = 'good' THEN 1 ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN feedback IS NULL OR feedback = 'medium' THEN 1 ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN feedback = 'bad' THEN 1 ELSE 0 END), 0)
                    FROM sofia_query_analytics
                    WHERE module_id = %s AND created_at >= %s
                    """,
                    (row[0], since),
                ).fetchone()
            summary = _quality_summary(*(int(value or 0) for value in counts))
            return {
                "analytics_id": analytics_id,
                "module_id": row[0],
                "theme": row[1],
                "provider": row[2],
                "feedback": row[3],
                "source_names": _decode_sources(row[4]),
                "period_days": safe_days,
                **summary,
            }
        except Exception:
            logger.debug("PostgreSQL feedback assessment failed; using SQLite fallback", exc_info=True)

    path = database_path(root)
    if not path.exists():
        return None
    initialize_analytics_store(root)
    since = (datetime.now(UTC) - timedelta(days=safe_days)).isoformat()
    connection = sqlite3.connect(path)
    try:
        row = connection.execute(
            "SELECT module_id, theme, provider, feedback, source_names FROM query_analytics WHERE id = ? AND (user_code = ? OR user_code IS NULL)",
            (analytics_id, user_code),
        ).fetchone()
        if not row:
            return None
        counts = connection.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN feedback = 'good' THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN feedback IS NULL OR feedback = 'medium' THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN feedback = 'bad' THEN 1 ELSE 0 END), 0)
            FROM query_analytics
            WHERE module_id = ? AND created_at >= ?
            """,
            (row[0], since),
        ).fetchone()
    finally:
        connection.close()
    summary = _quality_summary(*(int(value or 0) for value in counts))
    return {
        "analytics_id": analytics_id,
        "module_id": row[0],
        "theme": row[1],
        "provider": row[2],
        "feedback": row[3],
        "source_names": _decode_sources(row[4]),
        "period_days": safe_days,
        **summary,
    }


def record_learning_event(
    root: Path,
    assessment: dict[str, Any],
    retry_requested: bool,
    training_scheduled: bool,
) -> bool:
    """Persist a local, content-minimized learning signal.

    Source identifiers are kept so the module can explain which offline
    material contributed to the signal. Prompts, answers and clinical values
    are never copied into this event store.
    """
    sources = json.dumps(assessment.get("source_names", [])[:20], ensure_ascii=False)
    created_at = datetime.now(UTC)
    dsn = _postgres_dsn()
    if dsn and psycopg is not None:
        try:
            with psycopg.connect(dsn, connect_timeout=5) as connection:
                connection.execute(
                    """
                    INSERT INTO sofia_learning_events
                    (analytics_id, module_id, theme, feedback, provider, source_names, retry_requested, training_scheduled, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        assessment["analytics_id"],
                        assessment["module_id"],
                        assessment["theme"],
                        assessment["feedback"],
                        assessment["provider"],
                        sources,
                        retry_requested,
                        training_scheduled,
                        created_at,
                    ),
                )
                connection.commit()
            return True
        except Exception:
            logger.debug("PostgreSQL learning event failed; using SQLite fallback", exc_info=True)
    initialize_analytics_store(root)
    connection = sqlite3.connect(database_path(root))
    try:
        connection.execute(
            """
            INSERT INTO learning_events
            (analytics_id, module_id, theme, feedback, provider, source_names, retry_requested, training_scheduled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assessment["analytics_id"],
                assessment["module_id"],
                assessment["theme"],
                assessment["feedback"],
                assessment["provider"],
                sources,
                int(retry_requested),
                int(training_scheduled),
                created_at.isoformat(),
            ),
        )
        connection.commit()
        return True
    finally:
        connection.close()


def _report_payload(
    safe_days: int,
    module_id: str | None,
    total: int,
    rows: list[tuple[Any, ...]],
    user_rows: list[tuple[Any, ...]],
    storage: str,
    feedback_totals: tuple[Any, ...] | None = None,
) -> dict[str, Any]:
    top_themes = []
    for row in rows:
        good_answers = int(row[7] or 0)
        neutral_answers = int(row[8] or 0)
        bad_answers = int(row[9] or 0)
        evaluated_answers = good_answers + bad_answers
        top_themes.append(
            {
                "module_id": row[0],
                "theme": row[1],
                "intent": row[2],
                "consultations": int(row[3]),
                "last_consulted_at": row[4].isoformat() if hasattr(row[4], "isoformat") else row[4],
                "source_uses": int(row[5] or 0),
                "verified_consultations": int(row[6] or 0),
                "good_answers": good_answers,
                "medium_answers": neutral_answers,
                "bad_answers": bad_answers,
                "evaluated_answers": evaluated_answers,
                # NULL/medium is a neutral observation. It must not reduce
                # quality or request model improvement.
                "quality_score": None if row[10] is None else round(float(row[10]), 3),
                "needs_improvement": evaluated_answers > 0 and bad_answers > good_answers,
            }
        )
    by_module: list[dict[str, Any]] = []
    for item in top_themes:
        existing = next((entry for entry in by_module if entry["module_id"] == item["module_id"]), None)
        if existing is None:
            existing = {"module_id": item["module_id"], "consultations": 0, "themes": []}
            by_module.append(existing)
        existing["consultations"] += item["consultations"]
        existing["themes"].append({"theme": item["theme"], "consultations": item["consultations"]})
    by_user = [
        {"user_code": row[0] or "não identificado", "consultations": int(row[1]), "themes": int(row[2] or 0)}
        for row in user_rows
    ]
    feedback_summary = _quality_summary(
        *(int(value or 0) for value in (feedback_totals or (0, 0, 0)))
    )
    return {
        "period_days": safe_days,
        "module_id": module_id,
        "total_queries": int(total or 0),
        "top_themes": top_themes,
        "by_module": by_module,
        "by_user": by_user,
        "feedback_summary": feedback_summary,
        "storage": storage,
        "stores_raw_content": False,
    }


def theme_report(root: Path, module_id: str | None = None, days: int = 30, limit: int = 12) -> dict[str, Any]:
    """Return aggregate consultation themes without exposing raw content."""
    safe_days = max(1, min(int(days), 365))
    safe_limit = max(1, min(int(limit), 50))
    dsn = _postgres_dsn()
    if dsn and psycopg is not None:
        since = datetime.now(UTC) - timedelta(days=safe_days)
        where = "WHERE created_at >= %s"
        params: list[Any] = [since]
        if module_id:
            where += " AND module_id = %s"
            params.append(module_id)
        try:
            with psycopg.connect(dsn, connect_timeout=5) as connection:
                rows = connection.execute(
                    f"""
                    SELECT module_id, theme, intent, COUNT(*) AS consultations,
                           MAX(created_at) AS last_consulted_at,
                           SUM(source_count) AS source_uses,
                           SUM(verified::int) AS verified_consultations,
                           SUM(CASE WHEN feedback = 'good' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN feedback IS NULL OR feedback = 'medium' THEN 1 ELSE 0 END),
                           SUM(CASE WHEN feedback = 'bad' THEN 1 ELSE 0 END),
                           AVG(CASE feedback WHEN 'good' THEN 1.0 WHEN 'bad' THEN 0.0 END)
                    FROM sofia_query_analytics
                    {where}
                    GROUP BY module_id, theme, intent
                    ORDER BY consultations DESC, last_consulted_at DESC
                    LIMIT %s
                    """,
                    [*params, safe_limit],
                ).fetchall()
                user_rows = connection.execute(
                    f"SELECT user_code, COUNT(*) AS consultations, COUNT(DISTINCT theme) AS themes FROM sofia_query_analytics {where} GROUP BY user_code ORDER BY consultations DESC LIMIT %s",
                    [*params, safe_limit],
                ).fetchall()
                total = connection.execute(f"SELECT COUNT(*) FROM sofia_query_analytics {where}", params).fetchone()[0]
                feedback_totals = connection.execute(
                    f"""
                    SELECT
                        COALESCE(SUM(CASE WHEN feedback = 'good' THEN 1 ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN feedback IS NULL OR feedback = 'medium' THEN 1 ELSE 0 END), 0),
                        COALESCE(SUM(CASE WHEN feedback = 'bad' THEN 1 ELSE 0 END), 0)
                    FROM sofia_query_analytics {where}
                    """,
                    params,
                ).fetchone()
            return _report_payload(safe_days, module_id, int(total or 0), rows, user_rows, "postgresql", feedback_totals)
        except Exception:
            logger.debug("PostgreSQL analytics report unavailable; using SQLite fallback", exc_info=True)
    path = database_path(root)
    if not path.exists():
        return {
            "period_days": safe_days,
            "module_id": module_id,
            "total_queries": 0,
            "top_themes": [],
            "by_module": [],
            "by_user": [],
            "feedback_summary": _quality_summary(0, 0, 0),
            "storage": "sqlite",
            "stores_raw_content": False,
        }
    since = (datetime.now(UTC) - timedelta(days=safe_days)).isoformat()
    initialize_analytics_store(root)
    where = "WHERE created_at >= ?"
    params: list[Any] = [since]
    if module_id:
        where += " AND module_id = ?"
        params.append(module_id)
    connection = sqlite3.connect(path)
    try:
        rows = connection.execute(
            f"""
            SELECT module_id, theme, intent, COUNT(*) AS consultations,
                   MAX(created_at) AS last_consulted_at,
                   SUM(source_count) AS source_uses,
                   SUM(verified) AS verified_consultations,
                   SUM(CASE WHEN feedback = 'good' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN feedback IS NULL OR feedback = 'medium' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN feedback = 'bad' THEN 1 ELSE 0 END),
                   AVG(CASE feedback WHEN 'good' THEN 1.0 WHEN 'bad' THEN 0.0 END)
            FROM query_analytics
            {where}
            GROUP BY module_id, theme, intent
            ORDER BY consultations DESC, last_consulted_at DESC
            LIMIT ?
            """,
            [*params, safe_limit],
        ).fetchall()
        user_rows = connection.execute(
            f"SELECT user_code, COUNT(*) AS consultations, COUNT(DISTINCT theme) AS themes FROM query_analytics {where} GROUP BY user_code ORDER BY consultations DESC LIMIT ?",
            [*params, safe_limit],
        ).fetchall()
        total = connection.execute(f"SELECT COUNT(*) FROM query_analytics {where}", params).fetchone()[0]
        feedback_totals = connection.execute(
            f"""
            SELECT
                COALESCE(SUM(CASE WHEN feedback = 'good' THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN feedback IS NULL OR feedback = 'medium' THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN feedback = 'bad' THEN 1 ELSE 0 END), 0)
            FROM query_analytics {where}
            """,
            params,
        ).fetchone()
    finally:
        connection.close()
    return _report_payload(safe_days, module_id, int(total or 0), rows, user_rows, "sqlite", feedback_totals)
