from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import io
import json
import os
import secrets
import sqlite3
import threading
import time
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import qrcode
from fastapi import HTTPException, Request

from .pg_runtime import is_postgres, postgres_connection
from .secure_storage import decrypt_text, protect_for_storage

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "sofia.sqlite3"
ADMIN_CODE = "AG000001"
PBKDF2_ITERATIONS = 240_000
SESSION_SECONDS = 8 * 60 * 60
SESSION_ROTATION_SECONDS = 10 * 60
ACTIVATION_SECONDS = 24 * 60 * 60
PASSWORD_RESET_SECONDS = 10 * 60
LOGIN_MAX_FAILURES = 5
LOGIN_LOCK_SECONDS = 60
DEFAULT_INACTIVE_LOCK_DAYS = 90
_runtime_secret = secrets.token_bytes(32)
_rate_lock = threading.Lock()
_rate_limits: dict[str, tuple[int, float]] = {}
PG_AUTH_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_code TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    email_lookup TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    must_change_password INTEGER NOT NULL DEFAULT 0,
    two_factor_secret TEXT,
    two_factor_enabled INTEGER NOT NULL DEFAULT 0,
    password_changed_at TEXT,
    last_login_at TEXT,
    last_seen_at TEXT,
    blocked_at TEXT,
    blocked_reason TEXT
);
CREATE TABLE IF NOT EXISTS user_module_access (
    user_code TEXT NOT NULL,
    module_id TEXT NOT NULL,
    PRIMARY KEY (user_code, module_id),
    FOREIGN KEY (user_code) REFERENCES users(user_code)
);
CREATE TABLE IF NOT EXISTS access_requests (
    id BIGSERIAL PRIMARY KEY,
    request_code TEXT NOT NULL UNIQUE,
    requested_user_code TEXT,
    requested_module TEXT,
    email TEXT NOT NULL,
    email_lookup TEXT NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    requested_scopes TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decided_by TEXT,
    decision_note TEXT
);
CREATE TABLE IF NOT EXISTS account_activation_tokens (
    token_hash TEXT PRIMARY KEY,
    user_code TEXT NOT NULL,
    expires_at BIGINT NOT NULL,
    password_set_at TEXT,
    used_at TEXT,
    FOREIGN KEY (user_code) REFERENCES users(user_code)
);
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    token_hash TEXT NOT NULL UNIQUE,
    user_code TEXT NOT NULL,
    expires_at BIGINT NOT NULL,
    created_at TEXT NOT NULL,
    revoked_at TEXT,
    last_seen_at TEXT,
    last_rotated_at TEXT
);
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_hash TEXT PRIMARY KEY,
    user_code TEXT NOT NULL,
    expires_at BIGINT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    used_at TEXT
);
CREATE TABLE IF NOT EXISTS auth_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email_lookup ON users(email_lookup);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_code, expires_at);
"""


@contextmanager
def _connection() -> Iterator[Any]:
    with postgres_connection() as primary:
        if primary is not None:
            yield primary
            return
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def _email_lookup(email: str) -> str:
    return hmac.new(
        _secret(), email.strip().casefold().encode("utf-8"), hashlib.sha256
    ).hexdigest()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def _password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _password_policy(password: str, bootstrap: bool = False) -> None:
    if (
        len(password) < 8
        or not any(char.isupper() for char in password)
        or not any(char.islower() for char in password)
        or not any(char.isdigit() for char in password)
    ):
        raise ValueError(
            "A senha deve ter pelo menos 8 caracteres, com maiúscula, minúscula e número"
        )
    if not bootstrap and not any(not char.isalnum() for char in password):
        raise ValueError(
            "A senha deve ter pelo menos 8 caracteres, incluindo um caractere especial"
        )


def _ensure_column(connection: Any, table: str, column: str, definition: str) -> None:
    if is_postgres(connection):
        exists = connection.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = %s AND column_name = %s",
            (table, column),
        ).fetchone()
        if not exists:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        return
    columns = {
        row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _normalize_scopes(scopes: list[str] | tuple[str, ...] | None) -> list[str]:
    normalized = sorted(
        {
            str(scope).strip().casefold()
            for scope in (scopes or [])
            if str(scope).strip()
        }
    )
    if "core" in normalized:
        return ["CORE"]
    return [
        scope
        for scope in normalized
        if all(char.isalnum() or char == "-" for char in scope)
    ]


def _set_scopes(connection: Any, user_code: str, scopes: list[str]) -> None:
    connection.execute(
        "DELETE FROM user_module_access WHERE user_code = ?", (user_code,)
    )
    connection.executemany(
        "INSERT INTO user_module_access (user_code, module_id) VALUES (?, ?)",
        [(user_code, scope) for scope in _normalize_scopes(scopes)],
    )


def _scopes(connection: Any, user_code: str) -> list[str]:
    rows = connection.execute(
        "SELECT module_id FROM user_module_access WHERE user_code = ? ORDER BY module_id",
        (user_code,),
    ).fetchall()
    return [str(row[0]) for row in rows]


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return (
            parsed.replace(tzinfo=UTC)
            if parsed.tzinfo is None
            else parsed.astimezone(UTC)
        )
    except ValueError:
        return None


def _inactive_lock_days(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        "SELECT setting_value FROM auth_settings WHERE setting_key = 'inactive_lock_days'"
    ).fetchone()
    try:
        return max(1, min(3650, int(row[0]))) if row else DEFAULT_INACTIVE_LOCK_DAYS
    except (TypeError, ValueError):
        return DEFAULT_INACTIVE_LOCK_DAYS


def enforce_inactivity_policy() -> int:
    """Block non-admin accounts whose last activity exceeds the configured limit."""
    now = datetime.now(UTC)
    blocked = 0
    with _connection() as connection:
        days = _inactive_lock_days(connection)
        cutoff = now - timedelta(days=days)
        rows = connection.execute(
            "SELECT user_code, role, created_at, last_login_at, last_seen_at FROM users WHERE active = 1 AND user_code != ?",
            (ADMIN_CODE,),
        ).fetchall()
        for row in rows:
            last_activity = _parse_timestamp(
                row["last_seen_at"] or row["last_login_at"] or row["created_at"]
            )
            if last_activity is None or last_activity >= cutoff:
                continue
            reason = f"Bloqueado por inatividade superior a {days} dias"
            connection.execute(
                "UPDATE users SET active = 0, blocked_at = ?, blocked_reason = ? WHERE user_code = ?",
                (_now(), reason, row["user_code"]),
            )
            connection.execute(
                "UPDATE sessions SET revoked_at = ? WHERE user_code = ? AND revoked_at IS NULL",
                (_now(), row["user_code"]),
            )
            blocked += 1
        connection.commit()
    return blocked


def get_inactivity_policy() -> dict[str, Any]:
    with _connection() as connection:
        return {
            "inactive_lock_days": _inactive_lock_days(connection),
            "admin_exempt": True,
        }


def set_inactivity_policy(days: int) -> dict[str, Any]:
    if days < 1 or days > 3650:
        raise ValueError("O período de inatividade deve estar entre 1 e 3650 dias")
    with _connection() as connection:
        connection.execute(
            "INSERT INTO auth_settings (setting_key, setting_value, updated_at) VALUES (?, ?, ?) ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value, updated_at = excluded.updated_at",
            ("inactive_lock_days", str(days), _now()),
        )
        connection.commit()
    blocked = enforce_inactivity_policy()
    return {"inactive_lock_days": days, "blocked_now": blocked, "admin_exempt": True}


def _touch_user(
    connection: sqlite3.Connection, user_code: str, login: bool = False
) -> None:
    timestamp = _now()
    if login:
        connection.execute(
            "UPDATE users SET last_login_at = ?, last_seen_at = ? WHERE user_code = ?",
            (timestamp, timestamp, user_code),
        )
    else:
        connection.execute(
            "UPDATE users SET last_seen_at = ? WHERE user_code = ?",
            (timestamp, user_code),
        )


def _module_prefix(module_id: str) -> str:
    plain = (
        unicodedata.normalize("NFKD", module_id)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    letters = "".join(char for char in plain.upper() if char.isalpha())
    if letters == "CORE":
        return "CR"
    return (letters[:2] or "US").ljust(2, "X")


def _next_user_code(connection: sqlite3.Connection, module_id: str) -> str:
    prefix = _module_prefix(module_id)
    rows = connection.execute(
        "SELECT user_code FROM users WHERE substr(user_code, 1, 2) = ?", (prefix,)
    ).fetchall()
    used = []
    for row in rows:
        value = str(row[0])
        if len(value) == 8 and value[2:].isdigit():
            used.append(int(value[2:]))
    next_number = max(used, default=0) + 1
    if next_number > 999_999:
        raise ValueError(f"Não há mais matrículas disponíveis para o prefixo {prefix}")
    return f"{prefix}{next_number:06d}"


def _initialize_user_store_postgres(
    connection: Any,
    admin_email: str,
    first_password: str,
    reset_password: bool,
    configured_totp: str,
) -> None:
    connection.executescript(PG_AUTH_SCHEMA)
    connection.execute(
        "INSERT INTO auth_settings (setting_key, setting_value, updated_at) VALUES (%s, %s, %s) ON CONFLICT(setting_key) DO NOTHING",
        ("inactive_lock_days", str(DEFAULT_INACTIVE_LOCK_DAYS), _now()),
    )
    existing = connection.execute(
        "SELECT * FROM users WHERE user_code = ?", (ADMIN_CODE,)
    ).fetchone()
    if existing is None:
        if not first_password:
            raise RuntimeError(
                "Configure SOFIA_ADMIN_FIRST_PASSWORD no .env antes do primeiro acesso do AG000001"
            )
        _password_policy(first_password, bootstrap=True)
        connection.execute(
            "INSERT INTO users (user_code, email, email_lookup, name, password_hash, role, must_change_password, two_factor_secret, two_factor_enabled, password_changed_at) VALUES (?, ?, ?, ?, ?, 'admin', 1, ?, ?, ?)",
            (
                ADMIN_CODE,
                protect_for_storage(admin_email),
                _email_lookup(admin_email),
                protect_for_storage("Administrador"),
                _hash_password(first_password),
                protect_for_storage(configured_totp) if configured_totp else None,
                1 if configured_totp else 0,
                _now(),
            ),
        )
    elif first_password and (
        int(existing["must_change_password"] or 0) == 1 or reset_password
    ):
        _password_policy(first_password, bootstrap=True)
        if reset_password:
            connection.execute(
                "UPDATE users SET password_hash = ?, email = ?, email_lookup = ?, must_change_password = 1, password_changed_at = ? WHERE user_code = ?",
                (
                    _hash_password(first_password),
                    protect_for_storage(admin_email),
                    _email_lookup(admin_email),
                    _now(),
                    ADMIN_CODE,
                ),
            )
        else:
            connection.execute(
                "UPDATE users SET password_hash = ?, email = ?, email_lookup = ?, must_change_password = 1, password_changed_at = ? WHERE user_code = ?",
                (
                    _hash_password(first_password),
                    protect_for_storage(admin_email),
                    _email_lookup(admin_email),
                    _now(),
                    ADMIN_CODE,
                ),
            )
    if configured_totp:
        connection.execute(
            "UPDATE users SET two_factor_secret = ?, two_factor_enabled = 1 WHERE user_code = ? AND (two_factor_secret IS NULL OR two_factor_secret = '')",
            (protect_for_storage(configured_totp), ADMIN_CODE),
        )
    _set_scopes(connection, ADMIN_CODE, ["CORE"])
    connection.commit()


def initialize_user_store() -> None:
    """Create/migrate the local auth store without embedding a usable password."""
    admin_email = os.getenv("SOFIA_ADMIN_EMAIL", "admin@sofia.ai").strip().casefold()
    first_password = os.getenv(
        "SOFIA_ADMIN_FIRST_PASSWORD", os.getenv("SOFIA_ADMIN_PASSWORD", "")
    ).strip()
    reset_password = os.getenv(
        "SOFIA_ADMIN_RESET_PASSWORD", "false"
    ).strip().casefold() in {"1", "true", "yes", "on"}
    configured_totp = (
        os.getenv("SOFIA_ADMIN_TOTP_SECRET", "").strip().replace(" ", "").upper()
    )
    with _connection() as connection:
        if is_postgres(connection):
            _initialize_user_store_postgres(
                connection, admin_email, first_password, reset_password, configured_totp
            )
            return
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_code TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _ensure_column(
            connection, "users", "must_change_password", "INTEGER NOT NULL DEFAULT 0"
        )
        _ensure_column(connection, "users", "two_factor_secret", "TEXT")
        _ensure_column(
            connection, "users", "two_factor_enabled", "INTEGER NOT NULL DEFAULT 0"
        )
        _ensure_column(connection, "users", "password_changed_at", "TEXT")
        _ensure_column(connection, "users", "last_login_at", "TEXT")
        _ensure_column(connection, "users", "last_seen_at", "TEXT")
        _ensure_column(connection, "users", "blocked_at", "TEXT")
        _ensure_column(connection, "users", "blocked_reason", "TEXT")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS user_module_access (user_code TEXT NOT NULL, module_id TEXT NOT NULL, PRIMARY KEY (user_code, module_id), FOREIGN KEY (user_code) REFERENCES users(user_code))"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_code TEXT NOT NULL UNIQUE,
                requested_user_code TEXT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                requested_scopes TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                decided_at TEXT,
                decided_by TEXT,
                decision_note TEXT
            )
            """
        )
        _ensure_column(connection, "access_requests", "requested_module", "TEXT")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS account_activation_tokens (
                token_hash TEXT PRIMARY KEY,
                user_code TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                password_set_at TEXT,
                used_at TEXT,
                FOREIGN KEY (user_code) REFERENCES users(user_code)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                token_hash TEXT NOT NULL UNIQUE,
                user_code TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                revoked_at TEXT
            )
            """
        )
        _ensure_column(connection, "sessions", "last_seen_at", "TEXT")
        _ensure_column(connection, "sessions", "last_rotated_at", "TEXT")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token_hash TEXT PRIMARY KEY,
                user_code TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_code) REFERENCES users(user_code)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO auth_settings (setting_key, setting_value, updated_at) VALUES (?, ?, ?)",
            ("inactive_lock_days", str(DEFAULT_INACTIVE_LOCK_DAYS), _now()),
        )
        existing = connection.execute(
            "SELECT * FROM users WHERE user_code = ?", (ADMIN_CODE,)
        ).fetchone()
        if existing is None:
            if not first_password:
                raise RuntimeError(
                    "Configure SOFIA_ADMIN_FIRST_PASSWORD no .env antes do primeiro acesso do AG000001"
                )
            _password_policy(first_password, bootstrap=True)
            connection.execute(
                "INSERT INTO users (user_code, email, name, password_hash, role, must_change_password, two_factor_secret, two_factor_enabled, password_changed_at) VALUES (?, ?, ?, ?, 'admin', 1, ?, ?, ?)",
                (
                    ADMIN_CODE,
                    admin_email,
                    "Administrador",
                    _hash_password(first_password),
                    configured_totp or None,
                    1 if configured_totp else 0,
                    _now(),
                ),
            )
        elif first_password and (
            int(existing["must_change_password"] or 0) == 1 or reset_password
        ):
            _password_policy(first_password, bootstrap=True)
            if reset_password:
                # A deliberate local reset returns the administrator to a clean
                # first-access state. This is intentionally opt-in so a normal
                # restart never disables an already enrolled second factor.
                connection.execute(
                    "UPDATE users SET password_hash = ?, email = ?, must_change_password = 1, password_changed_at = ? WHERE user_code = ?",
                    (_hash_password(first_password), admin_email, _now(), ADMIN_CODE),
                )
            else:
                connection.execute(
                    "UPDATE users SET password_hash = ?, email = ?, must_change_password = 1, password_changed_at = ? WHERE user_code = ?",
                    (_hash_password(first_password), admin_email, _now(), ADMIN_CODE),
                )
        if configured_totp:
            connection.execute(
                "UPDATE users SET two_factor_secret = ?, two_factor_enabled = 1 WHERE user_code = ? AND (two_factor_secret IS NULL OR two_factor_secret = '')",
                (configured_totp, ADMIN_CODE),
            )
        _set_scopes(connection, ADMIN_CODE, ["CORE"])
        connection.commit()


def _user_payload(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    return {
        "user_code": row["user_code"],
        "email": decrypt_text(row["email"]),
        "name": decrypt_text(row["name"]),
        "role": row["role"],
        "scopes": _scopes(connection, row["user_code"]),
        "must_change_password": bool(row["must_change_password"]),
        "two_factor_enabled": bool(row["two_factor_enabled"]),
        "active": bool(row["active"]),
        "last_login_at": row["last_login_at"],
        "last_seen_at": row["last_seen_at"],
        "blocked_at": row["blocked_at"],
        "blocked_reason": row["blocked_reason"],
    }


def login_allowed(key: str) -> bool:
    now = time.time()
    with _rate_lock:
        _, locked_until = _rate_limits.get(key, (0, 0.0))
        if locked_until > now:
            return False
        if locked_until:
            _rate_limits.pop(key, None)
    return True


def register_login_failure(key: str) -> None:
    with _rate_lock:
        failures, _ = _rate_limits.get(key, (0, 0.0))
        failures += 1
        _rate_limits[key] = (
            failures,
            time.time() + LOGIN_LOCK_SECONDS if failures >= LOGIN_MAX_FAILURES else 0.0,
        )


def register_login_success(key: str) -> None:
    with _rate_lock:
        _rate_limits.pop(key, None)


def authenticate(
    identifier: str, password: str, otp: str | None = None
) -> dict[str, Any] | None:
    enforce_inactivity_policy()
    normalized = identifier.strip().casefold()
    with _connection() as connection:
        if is_postgres(connection):
            row = connection.execute(
                "SELECT * FROM users WHERE (lower(user_code) = ? OR email_lookup = ?) AND active = 1",
                (normalized, _email_lookup(normalized)),
            ).fetchone()
        else:
            row = connection.execute(
                "SELECT * FROM users WHERE (lower(user_code) = ? OR lower(email) = ?) AND active = 1",
                (normalized, normalized),
            ).fetchone()
        if row is None or not _password_matches(password, row["password_hash"]):
            return None
        # Toda conta com segundo fator habilitado precisa apresentar o OTP.
        # Antes, essa condição era limitada ao administrador; contas novas
        # ativadas exibiam o QR, mas conseguiam entrar sem usá-lo.
        if int(row["two_factor_enabled"] or 0):
            if not otp:
                return {"requires_2fa": True}
            if not verify_totp(decrypt_text(str(row["two_factor_secret"] or "")), otp):
                return None
        _touch_user(connection, row["user_code"], login=True)
        connection.commit()
        return _user_payload(connection, row)


def create_user(
    email: str,
    name: str,
    password: str,
    role: str = "user",
    scopes: list[str] | None = None,
    primary_module: str | None = None,
    must_change_password: bool = False,
) -> dict[str, Any]:
    user = {"email": email.strip().casefold(), "name": name.strip(), "role": role}
    if not user["email"] or not user["name"]:
        raise ValueError("Usuário, e-mail e nome são obrigatórios")
    _password_policy(password)
    normalized_scopes = _normalize_scopes(scopes)
    if not normalized_scopes:
        raise ValueError("Informe pelo menos um módulo ou CORE")
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        user_code = _next_user_code(connection, primary_module or normalized_scopes[0])
        if is_postgres(connection):
            connection.execute(
                "INSERT INTO users (user_code, email, email_lookup, name, password_hash, role, must_change_password, password_changed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    user_code,
                    protect_for_storage(user["email"]),
                    _email_lookup(user["email"]),
                    protect_for_storage(user["name"]),
                    _hash_password(password),
                    user["role"],
                    int(must_change_password),
                    _now(),
                ),
            )
        else:
            connection.execute(
                "INSERT INTO users (user_code, email, name, password_hash, role, must_change_password, password_changed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    user_code,
                    user["email"],
                    user["name"],
                    _hash_password(password),
                    user["role"],
                    int(must_change_password),
                    _now(),
                ),
            )
        _set_scopes(connection, user_code, normalized_scopes)
        connection.commit()
    return {
        **user,
        "user_code": user_code,
        "scopes": normalized_scopes,
        "must_change_password": must_change_password,
    }


def change_password(user_code: str, current_password: str, new_password: str) -> None:
    _password_policy(new_password)
    with _connection() as connection:
        row = connection.execute(
            "SELECT password_hash FROM users WHERE user_code = ? AND active = 1",
            (user_code,),
        ).fetchone()
        if row is None or not _password_matches(current_password, row["password_hash"]):
            raise ValueError("Senha atual inválida")
        connection.execute(
            "UPDATE users SET password_hash = ?, must_change_password = 0, password_changed_at = ? WHERE user_code = ?",
            (_hash_password(new_password), _now(), user_code),
        )
        connection.commit()


def _secret() -> bytes:
    # Keep session signatures and deterministic email lookups stable across
    # restarts.  A dedicated secret is preferred; the encryption key is a safe
    # configured fallback for existing local installations.
    configured = (
        os.getenv("SOFIA_SESSION_SECRET", "").strip()
        or os.getenv(
            "SOFIA_ENCRYPTION_KEY", os.getenv("SOFIA_DATA_ENCRYPTION_KEY", "")
        ).strip()
    )
    return hashlib.sha256(
        configured.encode() if configured else _runtime_secret
    ).digest()


def _encode(value: dict[str, Any]) -> str:
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode(value: str) -> dict[str, Any]:
    return json.loads(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)))


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(user: dict[str, Any]) -> str:
    expires_at = int(time.time()) + SESSION_SECONDS
    session_id = secrets.token_urlsafe(18)
    payload = _encode(
        {"v": 3, "sid": session_id, "sub": user["user_code"], "exp": expires_at}
    )
    signature = hmac.new(_secret(), payload.encode(), hashlib.sha256).digest()
    token = f"{payload}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"
    with _connection() as connection:
        timestamp = _now()
        connection.execute(
            "INSERT INTO sessions (session_id, token_hash, user_code, expires_at, created_at, last_seen_at, last_rotated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                session_id,
                _token_hash(token),
                user["user_code"],
                expires_at,
                timestamp,
                timestamp,
                timestamp,
            ),
        )
        connection.execute(
            "DELETE FROM sessions WHERE expires_at < ? OR revoked_at IS NOT NULL",
            (int(time.time()),),
        )
        connection.commit()
    return token


def verify_session(token: str) -> dict[str, Any]:
    enforce_inactivity_policy()
    try:
        payload, encoded_signature = token.split(".", 1)
        expected = hmac.new(_secret(), payload.encode(), hashlib.sha256).digest()
        actual = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )
        data = _decode(payload)
        if (
            data.get("v") != 3
            or not hmac.compare_digest(expected, actual)
            or int(data.get("exp", 0)) < int(time.time())
        ):
            raise ValueError
        with _connection() as connection:
            session = connection.execute(
                "SELECT * FROM sessions WHERE session_id = ? AND token_hash = ? AND revoked_at IS NULL AND expires_at >= ?",
                (data.get("sid"), _token_hash(token), int(time.time())),
            ).fetchone()
            row = connection.execute(
                "SELECT * FROM users WHERE user_code = ? AND active = 1",
                (data.get("sub"),),
            ).fetchone()
            if session is None or row is None:
                raise ValueError
            _touch_user(connection, row["user_code"])
            connection.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE session_id = ?",
                (_now(), data["sid"]),
            )
            connection.commit()
            return _user_payload(connection, row) | {
                "sub": row["user_code"],
                "sid": data["sid"],
            }
    except (
        ValueError,
        TypeError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        sqlite3.Error,
    ):
        raise HTTPException(401, "Sessão inválida ou expirada") from None


def revoke_session(token: str) -> None:
    with _connection() as connection:
        connection.execute(
            "UPDATE sessions SET revoked_at = ? WHERE token_hash = ?",
            (_now(), _token_hash(token)),
        )
        connection.commit()


def rotate_session(token: str) -> dict[str, Any]:
    user = verify_session(token)
    new_token = create_session(user)
    revoke_session(token)
    return {
        "token": new_token,
        "rotates_in_seconds": SESSION_ROTATION_SECONDS,
        "expires_in_seconds": SESSION_SECONDS,
        "user": user,
    }


def list_users() -> list[dict[str, Any]]:
    enforce_inactivity_policy()
    now = int(time.time())
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM users ORDER BY role DESC, lower(name)"
        ).fetchall()
        result = []
        for row in rows:
            sessions = connection.execute(
                "SELECT token_hash, created_at, last_seen_at, last_rotated_at, expires_at FROM sessions WHERE user_code = ? AND revoked_at IS NULL AND expires_at >= ? ORDER BY last_seen_at DESC",
                (row["user_code"], now),
            ).fetchall()
            result.append(
                _user_payload(connection, row)
                | {
                    "session_count": len(sessions),
                    "tokens": [
                        {
                            "fingerprint": str(session["token_hash"])[:12].upper(),
                            "created_at": session["created_at"],
                            "last_seen_at": session["last_seen_at"],
                            "last_rotated_at": session["last_rotated_at"],
                            "expires_at": session["expires_at"],
                            "rotation_seconds": SESSION_ROTATION_SECONDS,
                        }
                        for session in sessions
                    ],
                }
            )
    return result


def set_user_active(
    user_code: str, active: bool, reason: str | None = None
) -> dict[str, Any]:
    normalized = user_code.strip().upper()
    if normalized == ADMIN_CODE:
        raise ValueError("A conta AG000001 não pode ser bloqueada por este painel")
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE user_code = ?", (normalized,)
        ).fetchone()
        if row is None:
            raise ValueError("Usuário não encontrado")
        if active:
            connection.execute(
                "UPDATE users SET active = 1, blocked_at = NULL, blocked_reason = NULL, last_seen_at = ? WHERE user_code = ?",
                (_now(), normalized),
            )
        else:
            connection.execute(
                "UPDATE users SET active = 0, blocked_at = ?, blocked_reason = ? WHERE user_code = ?",
                (_now(), reason or "Bloqueado pela administração", normalized),
            )
            connection.execute(
                "UPDATE sessions SET revoked_at = ? WHERE user_code = ? AND revoked_at IS NULL",
                (_now(), normalized),
            )
        connection.commit()
        updated = connection.execute(
            "SELECT * FROM users WHERE user_code = ?", (normalized,)
        ).fetchone()
        return _user_payload(connection, updated)


def create_password_reset_token(user_code: str, admin_code: str) -> dict[str, Any]:
    if admin_code != ADMIN_CODE:
        raise PermissionError("Somente AG000001 pode redefinir senhas")
    normalized = user_code.strip().upper()
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT * FROM users WHERE user_code = ? AND active = 1", (normalized,)
        ).fetchone()
        if row is None:
            raise ValueError("Usuário não encontrado ou bloqueado")
        connection.execute(
            "UPDATE password_reset_tokens SET used_at = ? WHERE user_code = ? AND used_at IS NULL",
            (_now(), normalized),
        )
        token = secrets.token_urlsafe(32)
        expires_at = int(time.time()) + PASSWORD_RESET_SECONDS
        connection.execute(
            "INSERT INTO password_reset_tokens (token_hash, user_code, expires_at, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
            (_token_hash(token), normalized, expires_at, _now(), admin_code),
        )
        connection.execute(
            "UPDATE users SET password_hash = ?, must_change_password = 1 WHERE user_code = ?",
            (_hash_password(secrets.token_urlsafe(32)), normalized),
        )
        connection.execute(
            "UPDATE sessions SET revoked_at = ? WHERE user_code = ? AND revoked_at IS NULL",
            (_now(), normalized),
        )
        connection.commit()
    return {
        "user_code": normalized,
        "reset_token": token,
        "expires_at": expires_at,
        "expires_in_seconds": PASSWORD_RESET_SECONDS,
    }


def _password_reset_row(
    connection: sqlite3.Connection, user_code: str, reset_token: str
) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM password_reset_tokens WHERE user_code = ? AND token_hash = ? AND used_at IS NULL AND expires_at >= ?",
        (user_code.strip().upper(), _token_hash(reset_token.strip()), int(time.time())),
    ).fetchone()


def reset_password_with_token(
    user_code: str, reset_token: str, new_password: str
) -> dict[str, Any]:
    _password_policy(new_password)
    normalized = user_code.strip().upper()
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        token = _password_reset_row(connection, normalized, reset_token)
        user = connection.execute(
            "SELECT * FROM users WHERE user_code = ? AND active = 1", (normalized,)
        ).fetchone()
        if token is None or user is None:
            raise ValueError(
                "Código ou token de reset inválido, expirado ou já utilizado"
            )
        timestamp = _now()
        connection.execute(
            "UPDATE users SET password_hash = ?, must_change_password = 0, password_changed_at = ?, last_seen_at = ? WHERE user_code = ?",
            (_hash_password(new_password), timestamp, timestamp, normalized),
        )
        connection.execute(
            "UPDATE password_reset_tokens SET used_at = ? WHERE token_hash = ?",
            (timestamp, token["token_hash"]),
        )
        connection.commit()
        return {
            "user_code": normalized,
            "two_factor_enabled": bool(user["two_factor_enabled"]),
        }


async def require_user(request: Request) -> dict[str, Any]:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(401, "Faça login para continuar")
    return verify_session(header[7:].strip())


def require_admin(user: dict[str, Any]) -> None:
    if user.get("sub") != ADMIN_CODE:
        raise HTTPException(403, "Somente AG000001 pode administrar acessos")


def has_module_access(user: dict[str, Any], module_id: str) -> bool:
    scopes = {str(scope).casefold() for scope in user.get("scopes", [])}
    return "core" in scopes or module_id.casefold() in scopes


def require_module_access(user: dict[str, Any], module_id: str) -> None:
    if not has_module_access(user, module_id):
        raise HTTPException(403, f"Sua conta não possui acesso ao módulo {module_id}")


def _totp_counter(timestamp: int | None = None) -> int:
    return int((timestamp or int(time.time())) // 30)


def _totp_code(secret: str, timestamp: int | None = None) -> str:
    padded = secret + "=" * (-len(secret) % 8)
    key = base64.b32decode(padded, casefold=True)
    digest = hmac.new(
        key, _totp_counter(timestamp).to_bytes(8, "big"), hashlib.sha1
    ).digest()
    offset = digest[-1] & 0x0F
    number = (
        int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF
    ) % 1_000_000
    return f"{number:06d}"


def _two_factor_artifact(user_code: str, secret: str) -> dict[str, Any]:
    issuer = "SOFIA Local"
    uri = f"otpauth://totp/{issuer}:{user_code}?secret={secret}&issuer={issuer}&algorithm=SHA1&digits=6&period=30"
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return {
        "user_code": user_code,
        "secret": secret,
        "otpauth_uri": uri,
        "qr_data_uri": f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('ascii')}",
        "enabled": False,
    }


def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code.isdigit() or len(code) != 6:
        return False
    try:
        return any(
            hmac.compare_digest(
                _totp_code(secret, int(time.time()) + offset * 30), code
            )
            for offset in (-1, 0, 1)
        )
    except (binascii.Error, ValueError):
        return False


def setup_two_factor(user_code: str) -> dict[str, Any]:
    with _connection() as connection:
        row = connection.execute(
            "SELECT two_factor_secret, two_factor_enabled FROM users WHERE user_code = ?",
            (user_code,),
        ).fetchone()
        if row is None:
            raise ValueError("Usuário não encontrado")
        secret = decrypt_text(str(row["two_factor_secret"] or "")) or base64.b32encode(
            secrets.token_bytes(20)
        ).decode().rstrip("=")
        connection.execute(
            "UPDATE users SET two_factor_secret = ?, two_factor_enabled = 0 WHERE user_code = ?",
            (protect_for_storage(secret), user_code),
        )
        connection.commit()
    return _two_factor_artifact(user_code, secret)


def enable_two_factor(user_code: str, code: str) -> None:
    with _connection() as connection:
        row = connection.execute(
            "SELECT two_factor_secret FROM users WHERE user_code = ?", (user_code,)
        ).fetchone()
        if row is None or not verify_totp(
            decrypt_text(str(row["two_factor_secret"] or "")), code
        ):
            raise ValueError("Código 2FA inválido")
        connection.execute(
            "UPDATE users SET two_factor_enabled = 1 WHERE user_code = ?", (user_code,)
        )
        connection.commit()


def create_access_request(
    name: str, email: str, requested_module: str, scopes: list[str]
) -> dict[str, Any]:
    if not name.strip() or not email.strip():
        raise ValueError("Nome e e-mail são obrigatórios")
    if not requested_module.strip():
        raise ValueError("Escolha o módulo principal da matrícula")
    normalized_scopes = _normalize_scopes(scopes)
    if not normalized_scopes:
        raise ValueError("Escolha pelo menos um módulo ou CORE")
    request_code = f"REQ-{secrets.token_hex(5).upper()}"
    with _connection() as connection:
        normalized_email = email.strip().casefold()
        normalized_name = name.strip()
        if is_postgres(connection):
            connection.execute(
                "INSERT INTO access_requests (request_code, requested_user_code, requested_module, email, email_lookup, name, password_hash, requested_scopes, created_at) VALUES (?, NULL, ?, ?, ?, ?, '', ?, ?)",
                (
                    request_code,
                    requested_module.strip().casefold(),
                    protect_for_storage(normalized_email),
                    _email_lookup(normalized_email),
                    protect_for_storage(normalized_name),
                    json.dumps(normalized_scopes),
                    _now(),
                ),
            )
        else:
            connection.execute(
                "INSERT INTO access_requests (request_code, requested_user_code, requested_module, email, name, password_hash, requested_scopes, created_at) VALUES (?, NULL, ?, ?, ?, '', ?, ?)",
                (
                    request_code,
                    requested_module.strip().casefold(),
                    normalized_email,
                    normalized_name,
                    json.dumps(normalized_scopes),
                    _now(),
                ),
            )
        connection.commit()
    return {
        "request_code": request_code,
        "status": "pending",
        "requested_scopes": normalized_scopes,
    }


def list_access_requests(status: str = "pending") -> list[dict[str, Any]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT id, request_code, requested_module, email, name, requested_scopes, status, created_at, decided_at, decided_by, decision_note FROM access_requests WHERE status = ? ORDER BY id DESC",
            (status,),
        ).fetchall()
    result = []
    for row in rows:
        item = {**dict(row), "requested_scopes": json.loads(row["requested_scopes"])}
        item["email"] = decrypt_text(str(item.get("email") or ""))
        item["name"] = decrypt_text(str(item.get("name") or ""))
        result.append(item)
    return result


def decide_access_request(
    request_id: int,
    approve: bool,
    scopes: list[str] | None,
    admin_code: str,
    decision_note: str | None = None,
) -> dict[str, Any]:
    if admin_code != ADMIN_CODE:
        raise PermissionError("Somente AG000001 pode decidir solicitações")
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT * FROM access_requests WHERE id = ? AND status = 'pending'",
            (request_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Solicitação pendente não encontrada")
        if not approve:
            connection.execute(
                "UPDATE access_requests SET status = 'rejected', password_hash = '', decided_at = ?, decided_by = ?, decision_note = ? WHERE id = ?",
                (_now(), admin_code, decision_note, request_id),
            )
            connection.commit()
            return {"request_id": request_id, "status": "rejected"}
        final_scopes = _normalize_scopes(scopes or json.loads(row["requested_scopes"]))
        if not final_scopes:
            raise ValueError("A aprovação precisa definir pelo menos um módulo ou CORE")
        final_code = _next_user_code(
            connection, str(row["requested_module"] or final_scopes[0])
        )
        activation_token = secrets.token_urlsafe(32)
        email = decrypt_text(str(row["email"] or ""))
        name = decrypt_text(str(row["name"] or ""))
        if is_postgres(connection):
            connection.execute(
                "INSERT INTO users (user_code, email, email_lookup, name, password_hash, role, must_change_password, password_changed_at) VALUES (?, ?, ?, ?, ?, 'user', 1, NULL)",
                (
                    final_code,
                    protect_for_storage(email),
                    _email_lookup(email),
                    protect_for_storage(name),
                    _hash_password(secrets.token_urlsafe(32)),
                ),
            )
        else:
            connection.execute(
                "INSERT INTO users (user_code, email, name, password_hash, role, must_change_password, password_changed_at) VALUES (?, ?, ?, ?, 'user', 1, NULL)",
                (final_code, email, name, _hash_password(secrets.token_urlsafe(32))),
            )
        _set_scopes(connection, final_code, final_scopes)
        connection.execute(
            "INSERT INTO account_activation_tokens (token_hash, user_code, expires_at) VALUES (?, ?, ?)",
            (
                _token_hash(activation_token),
                final_code,
                int(time.time()) + ACTIVATION_SECONDS,
            ),
        )
        connection.execute(
            "UPDATE access_requests SET status = 'approved', password_hash = '', decided_at = ?, decided_by = ?, decision_note = ? WHERE id = ?",
            (
                _now(),
                admin_code,
                decision_note
                or json.dumps({"user_code": final_code, "scopes": final_scopes}),
                request_id,
            ),
        )
        connection.commit()
        return {
            "request_id": request_id,
            "status": "approved",
            "user_code": final_code,
            "scopes": final_scopes,
            "activation_token": activation_token,
            "activation_expires_at": int(time.time()) + ACTIVATION_SECONDS,
        }


def _activation_row(
    connection: sqlite3.Connection, user_code: str, activation_token: str
) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM account_activation_tokens WHERE user_code = ? AND token_hash = ? AND used_at IS NULL AND expires_at >= ?",
        (
            user_code.strip().upper(),
            _token_hash(activation_token.strip()),
            int(time.time()),
        ),
    ).fetchone()


def activate_account(
    user_code: str, activation_token: str, new_password: str
) -> dict[str, Any]:
    _password_policy(new_password)
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        token = _activation_row(connection, user_code, activation_token)
        user = connection.execute(
            "SELECT * FROM users WHERE user_code = ? AND active = 1 AND must_change_password = 1",
            (user_code.strip().upper(),),
        ).fetchone()
        if token is None or user is None:
            raise ValueError(
                "Código ou token de ativação inválido, expirado ou já utilizado"
            )
        secret = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
        connection.execute(
            "UPDATE users SET password_hash = ?, must_change_password = 0, password_changed_at = ?, two_factor_secret = ?, two_factor_enabled = 0 WHERE user_code = ?",
            (
                _hash_password(new_password),
                _now(),
                protect_for_storage(secret),
                user_code.strip().upper(),
            ),
        )
        connection.execute(
            "UPDATE account_activation_tokens SET password_set_at = ? WHERE token_hash = ?",
            (_now(), token["token_hash"]),
        )
        connection.commit()
    return _two_factor_artifact(user_code.strip().upper(), secret)


def enable_activation_two_factor(
    user_code: str, activation_token: str, code: str
) -> None:
    with _connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        token = _activation_row(connection, user_code, activation_token)
        row = connection.execute(
            "SELECT password_changed_at, must_change_password, two_factor_secret FROM users WHERE user_code = ? AND active = 1",
            (user_code.strip().upper(),),
        ).fetchone()
        if token is None or row is None:
            raise ValueError(
                "Código ou token de ativação inválido, expirado ou já utilizado"
            )
        # Compatibility with activations created by the earlier local build:
        # the password and QR were already saved, but password_set_at was not.
        # The persisted user state is the source of truth in that case.
        if not token["password_set_at"] and (
            int(row["must_change_password"] or 0) != 0
            or not row["password_changed_at"]
            or not row["two_factor_secret"]
        ):
            raise ValueError("Ative a senha antes de validar o 2FA")
        if not token["password_set_at"]:
            connection.execute(
                "UPDATE account_activation_tokens SET password_set_at = ? WHERE token_hash = ?",
                (_now(), token["token_hash"]),
            )
        if not verify_totp(decrypt_text(str(row["two_factor_secret"] or "")), code):
            raise ValueError("Código 2FA inválido")
        connection.execute(
            # The password was created in the activation form. Older builds
            # could leave the bootstrap flag enabled even after the password
            # and TOTP were successfully configured, trapping the user in the
            # first-access screen after a valid login.
            "UPDATE users SET two_factor_enabled = 1, must_change_password = 0 WHERE user_code = ?",
            (user_code.strip().upper(),),
        )
        connection.execute(
            "UPDATE account_activation_tokens SET used_at = ? WHERE token_hash = ?",
            (_now(), token["token_hash"]),
        )
        connection.commit()
