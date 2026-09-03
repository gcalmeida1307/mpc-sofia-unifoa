"""Migrate SOFIA's local operational stores to the configured PostgreSQL.

The SQLite files are intentionally retained as a recoverable source.  This
script copies rows idempotently, encrypts sensitive payloads before insertion,
and never prints prompts, patient data, emails, tokens or document contents.
Run it after configuring ``SOFIA_POSTGRES_URL`` and
``SOFIA_ENCRYPTION_KEY`` in ``.env``.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from api.auth import PG_AUTH_SCHEMA, _email_lookup
from api.fhir import PG_SCHEMA as FHIR_SCHEMA
from api.insights import PG_SCHEMA as INSIGHTS_SCHEMA
from api.integrations import PG_SCHEMA as INTEGRATION_SCHEMA
from api.pg_runtime import postgres_connection
from api.privacy import PG_SCHEMA as PRIVACY_SCHEMA
from api.secure_storage import protect_for_storage


def rows(path: Path, table: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        try:
            return [
                dict(row)
                for row in connection.execute(f'SELECT * FROM "{table}"').fetchall()
            ]
        except sqlite3.Error:
            return []


def text(value: Any) -> str:
    return "" if value is None else str(value)


def integer(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def json_text(value: Any, default: str = "{}") -> str:
    if value in (None, ""):
        return default
    if isinstance(value, str):
        try:
            json.loads(value)
            return value
        except (TypeError, ValueError):
            return default
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def iso_timestamp(value: Any) -> str:
    raw = text(value)
    if not raw:
        return datetime.now().astimezone().isoformat()
    return raw


def migrate_auth(connection: Any) -> int:
    source = ROOT / "data" / "sofia.sqlite3"
    connection.executescript(PG_AUTH_SCHEMA)
    count = 0
    for item in rows(source, "users"):
        email = text(item.get("email")).strip().casefold()
        connection.execute(
            """
            INSERT INTO users (user_code, email, email_lookup, name, password_hash, role, active, created_at,
                must_change_password, two_factor_secret, two_factor_enabled, password_changed_at,
                last_login_at, last_seen_at, blocked_at, blocked_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_code) DO UPDATE SET email=excluded.email, email_lookup=excluded.email_lookup,
                name=excluded.name, password_hash=excluded.password_hash, role=excluded.role,
                active=excluded.active, created_at=excluded.created_at, must_change_password=excluded.must_change_password,
                two_factor_secret=excluded.two_factor_secret, two_factor_enabled=excluded.two_factor_enabled,
                password_changed_at=excluded.password_changed_at, last_login_at=excluded.last_login_at,
                last_seen_at=excluded.last_seen_at, blocked_at=excluded.blocked_at, blocked_reason=excluded.blocked_reason
            """,
            (
                text(item.get("user_code")).upper(),
                protect_for_storage(email),
                _email_lookup(email),
                protect_for_storage(text(item.get("name"))),
                text(item.get("password_hash")),
                text(item.get("role")) or "user",
                integer(item.get("active"), 1),
                iso_timestamp(item.get("created_at")),
                integer(item.get("must_change_password")),
                protect_for_storage(text(item.get("two_factor_secret")))
                if item.get("two_factor_secret")
                else None,
                integer(item.get("two_factor_enabled")),
                item.get("password_changed_at"),
                item.get("last_login_at"),
                item.get("last_seen_at"),
                item.get("blocked_at"),
                item.get("blocked_reason"),
            ),
        )
        count += 1
    for item in rows(source, "user_module_access"):
        connection.execute(
            "INSERT INTO user_module_access (user_code, module_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (text(item.get("user_code")).upper(), text(item.get("module_id"))),
        )
    for item in rows(source, "access_requests"):
        email = text(item.get("email")).strip().casefold()
        connection.execute(
            """
            INSERT INTO access_requests (id, request_code, requested_user_code, requested_module, email, email_lookup,
                name, password_hash, requested_scopes, status, created_at, decided_at, decided_by, decision_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(request_code) DO UPDATE SET requested_user_code=excluded.requested_user_code,
                requested_module=excluded.requested_module, email=excluded.email, email_lookup=excluded.email_lookup,
                name=excluded.name, password_hash=excluded.password_hash, requested_scopes=excluded.requested_scopes,
                status=excluded.status, created_at=excluded.created_at, decided_at=excluded.decided_at,
                decided_by=excluded.decided_by, decision_note=excluded.decision_note
            """,
            (
                integer(item.get("id")),
                text(item.get("request_code")),
                item.get("requested_user_code"),
                item.get("requested_module"),
                protect_for_storage(email),
                _email_lookup(email),
                protect_for_storage(text(item.get("name"))),
                text(item.get("password_hash")),
                json_text(item.get("requested_scopes"), "[]"),
                text(item.get("status")) or "pending",
                iso_timestamp(item.get("created_at")),
                item.get("decided_at"),
                item.get("decided_by"),
                item.get("decision_note"),
            ),
        )
    for table, columns, conflict in (
        (
            "account_activation_tokens",
            ("token_hash", "user_code", "expires_at", "password_set_at", "used_at"),
            "token_hash",
        ),
        (
            "password_reset_tokens",
            (
                "token_hash",
                "user_code",
                "expires_at",
                "created_at",
                "created_by",
                "used_at",
            ),
            "token_hash",
        ),
    ):
        for item in rows(source, table):
            values = tuple(item.get(column) for column in columns)
            placeholders = ", ".join("?" for _ in columns)
            assignments = ", ".join(
                f"{column}=excluded.{column}" for column in columns[1:]
            )
            connection.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT({conflict}) DO UPDATE SET {assignments}",
                values,
            )
    for item in rows(source, "sessions"):
        columns = (
            "session_id",
            "token_hash",
            "user_code",
            "expires_at",
            "created_at",
            "revoked_at",
            "last_seen_at",
            "last_rotated_at",
        )
        values = tuple(item.get(column) for column in columns)
        connection.execute(
            "INSERT INTO sessions (session_id, token_hash, user_code, expires_at, created_at, revoked_at, last_seen_at, last_rotated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET token_hash=excluded.token_hash, user_code=excluded.user_code, expires_at=excluded.expires_at, created_at=excluded.created_at, revoked_at=excluded.revoked_at, last_seen_at=excluded.last_seen_at, last_rotated_at=excluded.last_rotated_at",
            values,
        )
    for item in rows(source, "auth_settings"):
        connection.execute(
            "INSERT INTO auth_settings (setting_key, setting_value, updated_at) VALUES (?, ?, ?) ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=excluded.updated_at",
            (
                text(item.get("setting_key")),
                text(item.get("setting_value")),
                iso_timestamp(item.get("updated_at")),
            ),
        )
    connection.execute(
        "SELECT setval(pg_get_serial_sequence('access_requests', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM access_requests"
    )
    return count


def migrate_fhir(connection: Any) -> int:
    source = ROOT / "data" / "sofia.sqlite3"
    connection.executescript(FHIR_SCHEMA)
    items = rows(source, "fhir_resources")
    for item in items:
        connection.execute(
            "INSERT INTO fhir_resources (resource_type, resource_id, resource_json, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(resource_type, resource_id) DO UPDATE SET resource_json=excluded.resource_json, updated_at=excluded.updated_at",
            (
                text(item.get("resource_type")),
                text(item.get("resource_id")),
                protect_for_storage(text(item.get("resource_json"))),
                iso_timestamp(item.get("updated_at")),
            ),
        )
    return len(items)


def migrate_integrations(connection: Any) -> int:
    source = ROOT / "data" / "integrations.sqlite3"
    connection.executescript(INTEGRATION_SCHEMA)
    counts = 0
    for item in rows(source, "integration_jobs"):
        columns = (
            "id",
            "connector",
            "resource",
            "status",
            "started_at",
            "finished_at",
            "next_cursor",
            "inserted_count",
            "changed_count",
            "unchanged_count",
            "error",
        )
        connection.execute(
            f"INSERT INTO integration_jobs ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)}) ON CONFLICT(id) DO NOTHING",
            tuple(item.get(column) for column in columns),
        )
        counts += 1
    for item in rows(source, "integration_raw"):
        payload = text(item.get("payload_json"))
        connection.execute(
            "INSERT INTO integration_raw (id, connector, resource, external_id, payload_json, payload_hash, first_received_at, last_received_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(connector, resource, external_id) DO UPDATE SET payload_json=excluded.payload_json, payload_hash=excluded.payload_hash, last_received_at=excluded.last_received_at",
            (
                item.get("id"),
                text(item.get("connector")),
                text(item.get("resource")),
                text(item.get("external_id")),
                protect_for_storage(payload),
                text(item.get("payload_hash")),
                iso_timestamp(item.get("first_received_at")),
                iso_timestamp(item.get("last_received_at")),
            ),
        )
    for item in rows(source, "integration_checkpoints"):
        connection.execute(
            "INSERT INTO integration_checkpoints (connector, resource, cursor, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(connector, resource) DO UPDATE SET cursor=excluded.cursor, updated_at=excluded.updated_at",
            (
                text(item.get("connector")),
                text(item.get("resource")),
                item.get("cursor"),
                iso_timestamp(item.get("updated_at")),
            ),
        )
    for item in rows(source, "integration_dlq"):
        connection.execute(
            "INSERT INTO integration_dlq (id, job_id, connector, resource, payload_json, error, attempts, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
            (
                item.get("id"),
                item.get("job_id"),
                text(item.get("connector")),
                text(item.get("resource")),
                protect_for_storage(text(item.get("payload_json")))
                if item.get("payload_json")
                else None,
                text(item.get("error")),
                integer(item.get("attempts"), 1),
                text(item.get("status")) or "pending",
                iso_timestamp(item.get("created_at")),
            ),
        )
    for table in ("integration_jobs", "integration_raw", "integration_dlq"):
        connection.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table}"
        )
    return counts


def migrate_insights(connection: Any) -> int:
    source = ROOT / "data" / "insights.sqlite3"
    connection.executescript(INSIGHTS_SCHEMA)
    items = rows(source, "insights")
    for item in items:
        connection.execute(
            "INSERT INTO insights (id, module_id, kind, title, evidence_json, entities_json, confidence, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
            (
                item.get("id"),
                text(item.get("module_id")),
                text(item.get("kind")),
                text(item.get("title")),
                protect_for_storage(json_text(item.get("evidence_json"))),
                protect_for_storage(json_text(item.get("entities_json"))),
                float(item.get("confidence") or 0),
                text(item.get("status")),
                iso_timestamp(item.get("created_at")),
            ),
        )
    connection.execute(
        "SELECT setval(pg_get_serial_sequence('insights', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM insights"
    )
    return len(items)


def migrate_privacy(connection: Any) -> int:
    source = ROOT / "data" / "sofia.sqlite3"
    connection.executescript(PRIVACY_SCHEMA)
    items = rows(source, "audit_events")
    for item in items:
        connection.execute(
            "INSERT INTO audit_events (id, user_code, module_id, action, resource_id, created_at) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
            (
                item.get("id"),
                text(item.get("user_code")),
                item.get("module_id"),
                text(item.get("action")),
                item.get("resource_id"),
                iso_timestamp(item.get("created_at")),
            ),
        )
    connection.execute(
        "SELECT setval(pg_get_serial_sequence('audit_events', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM audit_events"
    )
    return len(items)


def migrate_analytics_and_observability(connection: Any) -> tuple[int, int]:
    analytics_db = ROOT / "data" / "agent_memory.sqlite3"
    connection.raw.execute("SET search_path TO public")
    connection.raw.execute(
        """CREATE TABLE IF NOT EXISTS sofia_query_analytics (id BIGSERIAL PRIMARY KEY, module_id TEXT NOT NULL, user_code TEXT, theme TEXT NOT NULL, intent TEXT NOT NULL, source_count INTEGER NOT NULL DEFAULT 0, provider TEXT NOT NULL, verified BOOLEAN NOT NULL DEFAULT FALSE, feedback TEXT, source_names TEXT NOT NULL DEFAULT '', created_at TIMESTAMPTZ NOT NULL)"""
    )
    connection.raw.execute(
        """CREATE TABLE IF NOT EXISTS sofia_learning_events (id BIGSERIAL PRIMARY KEY, analytics_id BIGINT NOT NULL, module_id TEXT NOT NULL, theme TEXT NOT NULL, feedback TEXT NOT NULL, provider TEXT NOT NULL, source_names TEXT NOT NULL DEFAULT '', retry_requested BOOLEAN NOT NULL DEFAULT FALSE, training_scheduled BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL)"""
    )
    query_items = rows(analytics_db, "query_analytics")
    for item in query_items:
        connection.raw.execute(
            "INSERT INTO sofia_query_analytics (id, module_id, user_code, theme, intent, source_count, provider, verified, feedback, source_names, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT(id) DO NOTHING",
            (
                item.get("id"),
                text(item.get("module_id")),
                item.get("user_code"),
                text(item.get("theme")),
                text(item.get("intent")),
                integer(item.get("source_count")),
                text(item.get("provider")),
                bool(item.get("verified")),
                item.get("feedback"),
                text(item.get("source_names")),
                iso_timestamp(item.get("created_at")),
            ),
        )
    for item in rows(analytics_db, "learning_events"):
        connection.raw.execute(
            "INSERT INTO sofia_learning_events (id, analytics_id, module_id, theme, feedback, provider, source_names, retry_requested, training_scheduled, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT(id) DO NOTHING",
            (
                item.get("id"),
                item.get("analytics_id"),
                text(item.get("module_id")),
                text(item.get("theme")),
                text(item.get("feedback")),
                text(item.get("provider")),
                text(item.get("source_names")),
                bool(item.get("retry_requested")),
                bool(item.get("training_scheduled")),
                iso_timestamp(item.get("created_at")),
            ),
        )
    trace_db = ROOT / "data" / "observability.sqlite3"
    connection.raw.execute(
        """CREATE TABLE IF NOT EXISTS sofia_traces (trace_id TEXT PRIMARY KEY, request_hash TEXT NOT NULL, user_code TEXT, module_id TEXT, intent TEXT, complexity TEXT, router TEXT, provider TEXT, model TEXT, status TEXT NOT NULL, confidence DOUBLE PRECISION, started_at TIMESTAMPTZ NOT NULL, finished_at TIMESTAMPTZ, latency_ms DOUBLE PRECISION, metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb)"""
    )
    connection.raw.execute(
        """CREATE TABLE IF NOT EXISTS sofia_trace_spans (id BIGSERIAL PRIMARY KEY, trace_id TEXT NOT NULL REFERENCES sofia_traces(trace_id) ON DELETE CASCADE, stage TEXT NOT NULL, status TEXT NOT NULL, started_at TIMESTAMPTZ NOT NULL, finished_at TIMESTAMPTZ, latency_ms DOUBLE PRECISION, metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb)"""
    )
    trace_items = rows(trace_db, "traces")
    for item in trace_items:
        connection.raw.execute(
            "INSERT INTO sofia_traces (trace_id, request_hash, user_code, module_id, intent, complexity, router, provider, model, status, confidence, started_at, finished_at, latency_ms, metrics_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb) ON CONFLICT(trace_id) DO NOTHING",
            (
                text(item.get("trace_id")),
                text(item.get("request_hash")),
                item.get("user_code"),
                item.get("module_id"),
                item.get("intent"),
                item.get("complexity"),
                item.get("router"),
                item.get("provider"),
                item.get("model"),
                text(item.get("status")),
                item.get("confidence"),
                iso_timestamp(item.get("started_at")),
                item.get("finished_at"),
                item.get("latency_ms"),
                json_text(item.get("metrics_json")),
            ),
        )
    span_items = rows(trace_db, "trace_spans")
    for item in span_items:
        connection.raw.execute(
            "INSERT INTO sofia_trace_spans (id, trace_id, stage, status, started_at, finished_at, latency_ms, metrics_json) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb) ON CONFLICT(id) DO NOTHING",
            (
                item.get("id"),
                text(item.get("trace_id")),
                text(item.get("stage")),
                text(item.get("status")),
                iso_timestamp(item.get("started_at")),
                item.get("finished_at"),
                item.get("latency_ms"),
                json_text(item.get("metrics_json")),
            ),
        )
    for table in ("sofia_query_analytics", "sofia_learning_events", "sofia_trace_spans"):
        connection.raw.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM {table}"
        )
    return len(query_items), len(trace_items)


def main() -> int:
    with postgres_connection(required=True) as connection:
        auth = migrate_auth(connection)
        fhir = migrate_fhir(connection)
        integrations = migrate_integrations(connection)
        insights = migrate_insights(connection)
        privacy = migrate_privacy(connection)
        analytics, traces = migrate_analytics_and_observability(connection)
        connection.raw.execute("SET search_path TO sofia_runtime")
        connection.commit()
    print(
        f"Migração concluída: auth={auth}, fhir={fhir}, integrations={integrations}, insights={insights}, audit={privacy}, analytics={analytics}, traces={traces}. SQLite preservado."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
