from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO

from config.settings import settings

IDLE_MINUTES = 15


class AuthService:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or settings.POSTGRES_DSN

    def connect(self):
        return psycopg.connect(self.dsn)

    def ensure_schema(self) -> bool:
        statements = [
            """CREATE TABLE IF NOT EXISTS auth_users (
                id BIGSERIAL PRIMARY KEY, username TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin','user')), status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','active','revoked')), password_hash TEXT, totp_secret TEXT,
                authorized_tools JSONB NOT NULL DEFAULT '[]'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                approved_at TIMESTAMPTZ, approved_by BIGINT REFERENCES auth_users(id), last_login_at TIMESTAMPTZ)""",
            """CREATE TABLE IF NOT EXISTS auth_sessions (
                id UUID PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES auth_users(id), token_hash TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMPTZ NOT NULL, revoked_at TIMESTAMPTZ, ip_address TEXT, user_agent TEXT)""",
            """CREATE TABLE IF NOT EXISTS access_requests (
                id BIGSERIAL PRIMARY KEY, username TEXT NOT NULL, display_name TEXT NOT NULL, email TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','approved','rejected')), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                reviewed_at TIMESTAMPTZ, reviewed_by BIGINT REFERENCES auth_users(id), UNIQUE(username, status))""",
            """CREATE TABLE IF NOT EXISTS auth_audit_log (
                id BIGSERIAL PRIMARY KEY, user_id BIGINT REFERENCES auth_users(id), username TEXT, action TEXT NOT NULL,
                success BOOLEAN NOT NULL, ip_address TEXT, metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""",
            """CREATE INDEX IF NOT EXISTS auth_sessions_token_idx ON auth_sessions(token_hash)
                WHERE revoked_at IS NULL""",
        ]
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    for statement in statements:
                        cur.execute(statement)
                    cur.execute("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS setup_token_hash TEXT")
                    cur.execute("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS email TEXT")
                    cur.execute("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS password_reset_token_hash TEXT")
                    cur.execute("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMPTZ")
                    cur.execute("ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS password_reset_required BOOLEAN NOT NULL DEFAULT FALSE")
                    cur.execute("""INSERT INTO auth_users (username, display_name, role, status)
                        VALUES ('glauco.almeida', 'Glauco Almeida', 'admin', 'pending')
                        ON CONFLICT (username) DO NOTHING""")
                    if settings.AUTH_BOOTSTRAP_TOKEN:
                        cur.execute("""UPDATE auth_users SET setup_token_hash=%s
                            WHERE username='glauco.almeida' AND status='pending' AND password_hash IS NULL""",
                            (self.token_hash(settings.AUTH_BOOTSTRAP_TOKEN),))
                conn.commit()
            return True
        except Exception:
            return False

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[^A-Za-z0-9]', password):
            raise ValueError('A senha deve ter 8+ caracteres, maiúscula, minúscula e símbolo')

    @staticmethod
    def validate_email(email: str) -> str:
        normalized = email.lower().strip()
        if len(normalized) > 200 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', normalized):
            raise ValueError('Informe um e-mail valido')
        return normalized

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
        return 'pbkdf2_sha256$310000$' + base64.b64encode(salt).decode() + '$' + base64.b64encode(digest).decode()

    @staticmethod
    def verify_password(password: str, encoded: str | None) -> bool:
        if not encoded:
            return False
        try:
            _, rounds, salt, expected = encoded.split('$')
            actual = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(salt), int(rounds))
            return hmac.compare_digest(actual, base64.b64decode(expected))
        except Exception:
            return False

    @staticmethod
    def token_hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def audit(self, username: str | None, action: str, success: bool, ip: str | None = None, user_id: int | None = None) -> None:
        try:
            with self.connect() as conn:
                conn.execute("INSERT INTO auth_audit_log (user_id, username, action, success, ip_address) VALUES (%s,%s,%s,%s,%s)", (user_id, username, action, success, ip))
                conn.commit()
        except Exception:
            pass

    def enrollment(self, username: str, invite_token: str) -> dict[str, str] | None:
        self.ensure_schema()
        normalized = username.lower().strip()
        with self.connect() as conn:
            row = conn.execute("SELECT status, password_hash, setup_token_hash FROM auth_users WHERE username=%s", (normalized,)).fetchone()
            if not row or row[0] != 'pending' or row[1] or not row[2] or not hmac.compare_digest(self.token_hash(invite_token), row[2]):
                return None
            secret = pyotp.random_base32()
            conn.execute("UPDATE auth_users SET totp_secret=%s WHERE username=%s AND status='pending'", (secret, normalized))
            conn.commit()
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name='SOFIA')
        image = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
        buffer = BytesIO()
        image.save(buffer)
        qr_code_data_url = 'data:image/svg+xml;base64,' + base64.b64encode(buffer.getvalue()).decode()
        return {'secret': secret, 'provisioning_uri': provisioning_uri, 'qr_code_data_url': qr_code_data_url}

    def complete_first_access(self, username: str, password: str, otp: str, ip: str | None = None) -> bool:
        self.validate_password(password)
        normalized = username.lower().strip()
        with self.connect() as conn:
            row = conn.execute("SELECT totp_secret FROM auth_users WHERE username=%s AND status='pending' AND password_hash IS NULL", (normalized,)).fetchone()
            if not row or not row[0] or not pyotp.TOTP(row[0]).verify(otp, valid_window=1):
                return False
            cur = conn.execute("""UPDATE auth_users SET password_hash=%s, status='active', approved_at=NOW(), setup_token_hash=NULL
                WHERE username=%s AND status='pending' AND password_hash IS NULL""", (self.hash_password(password), normalized))
            conn.commit()
        self.audit(username, 'first_access', cur.rowcount == 1, ip)
        return cur.rowcount == 1

    def login(self, username: str, password: str, otp: str, ip: str | None, user_agent: str | None) -> dict[str, Any] | None:
        self.ensure_schema()
        with self.connect() as conn:
            row = conn.execute("SELECT id, username, display_name, role, status, password_hash, totp_secret, authorized_tools, email, password_reset_required FROM auth_users WHERE username=%s", (username.lower().strip(),)).fetchone()
        if not row or row[4] != 'active' or row[9] or not self.verify_password(password, row[5]) or not row[6] or not pyotp.TOTP(row[6]).verify(otp, valid_window=1):
            self.audit(username, 'login', False, ip)
            return None
        token = secrets.token_urlsafe(48); now = datetime.now(timezone.utc); expires = now + timedelta(minutes=IDLE_MINUTES)
        with self.connect() as conn:
            conn.execute("INSERT INTO auth_sessions (id,user_id,token_hash,expires_at,ip_address,user_agent) VALUES (gen_random_uuid(),%s,%s,%s,%s,%s)", (row[0], self.token_hash(token), expires, ip, user_agent))
            conn.execute("UPDATE auth_users SET last_login_at=NOW() WHERE id=%s", (row[0],)); conn.commit()
        self.audit(row[1], 'login', True, ip, row[0])
        return {'token': token, 'expires_in': IDLE_MINUTES * 60, 'user': {'id': row[0], 'username': row[1], 'display_name': row[2], 'role': row[3], 'authorized_tools': row[7] or [], 'email': row[8], 'email_required': not bool(row[8])}}

    def authenticate(self, token: str) -> dict[str, Any] | None:
        if not token: return None
        with self.connect() as conn:
            row = conn.execute("""SELECT u.id,u.username,u.display_name,u.role,u.authorized_tools,s.id,u.email,u.password_reset_required
                FROM auth_sessions s JOIN auth_users u ON u.id=s.user_id
                WHERE s.token_hash=%s AND s.revoked_at IS NULL AND s.expires_at>NOW() AND u.status='active'""", (self.token_hash(token),)).fetchone()
            if not row: return None
            conn.execute("UPDATE auth_sessions SET last_activity_at=NOW(), expires_at=NOW()+(%s * INTERVAL '1 minute') WHERE id=%s", (IDLE_MINUTES, row[5])); conn.commit()
        return {'id': row[0], 'username': row[1], 'display_name': row[2], 'role': row[3], 'authorized_tools': row[4] or [], 'email': row[6], 'email_required': not bool(row[6]), 'password_reset_required': row[7]}

    def logout(self, token: str) -> bool:
        with self.connect() as conn:
            cur=conn.execute("UPDATE auth_sessions SET revoked_at=NOW() WHERE token_hash=%s AND revoked_at IS NULL", (self.token_hash(token),)); conn.commit(); return cur.rowcount > 0

    def request_access(self, username: str, display_name: str, email: str, reason: str) -> int:
        self.ensure_schema()
        email=self.validate_email(email)
        with self.connect() as conn:
            row=conn.execute("INSERT INTO access_requests(username,display_name,email,reason) VALUES(%s,%s,%s,%s) RETURNING id", (username.lower().strip(),display_name.strip(),email.lower().strip(),reason.strip())).fetchone(); conn.commit(); return row[0]

    def list_requests(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows=conn.execute("SELECT id,username,display_name,email,reason,status,created_at FROM access_requests ORDER BY created_at DESC").fetchall()
        return [{'id':r[0],'username':r[1],'display_name':r[2],'email':r[3],'reason':r[4],'status':r[5],'created_at':r[6].isoformat()} for r in rows]

    def approve_request(self, request_id: int, admin_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row=conn.execute("SELECT username,display_name,email FROM access_requests WHERE id=%s AND status='pending' FOR UPDATE",(request_id,)).fetchone()
            if not row: return None
            setup_token = secrets.token_urlsafe(24)
            conn.execute("""INSERT INTO auth_users(username,display_name,email,role,status,setup_token_hash) VALUES(%s,%s,%s,'user','pending',%s)
                ON CONFLICT(username) DO UPDATE SET display_name=EXCLUDED.display_name,email=EXCLUDED.email,status='pending',setup_token_hash=EXCLUDED.setup_token_hash""",(row[0],row[1],row[2],self.token_hash(setup_token)))
            conn.execute("UPDATE access_requests SET status='approved',reviewed_at=NOW(),reviewed_by=%s WHERE id=%s",(admin_id,request_id)); conn.commit()
            return {"approved": True, "setup_token": setup_token}

    def list_users(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows=conn.execute("SELECT id,username,display_name,role,status,authorized_tools,created_at,last_login_at,email,password_reset_required FROM auth_users ORDER BY created_at").fetchall()
        return [{'id':r[0],'username':r[1],'display_name':r[2],'role':r[3],'status':r[4],'authorized_tools':r[5] or [],'created_at':r[6].isoformat(),'last_login_at':r[7].isoformat() if r[7] else None,'email':r[8],'password_reset_required':r[9]} for r in rows]

    def update_profile(self, user_id: int, display_name: str, email: str) -> dict[str, Any]:
        normalized_email = self.validate_email(email)
        with self.connect() as conn:
            row=conn.execute("UPDATE auth_users SET display_name=%s,email=%s WHERE id=%s RETURNING username,display_name,email,role",(display_name.strip(),normalized_email,user_id)).fetchone();conn.commit()
        if not row: raise ValueError('Usuario nao encontrado')
        return {'username':row[0],'display_name':row[1],'email':row[2],'role':row[3]}

    def admin_notification_emails(self) -> list[str]:
        with self.connect() as conn:
            rows=conn.execute("SELECT email FROM auth_users WHERE role='admin' AND status='active' AND email IS NOT NULL").fetchall()
        configured=os.getenv('ADMIN_NOTIFICATION_EMAIL','').strip()
        return sorted({*(r[0] for r in rows if r[0]), *([configured] if configured else [])})

    def require_password_reset(self, user_id: int) -> dict[str, Any] | None:
        token=secrets.token_urlsafe(32)
        with self.connect() as conn:
            row=conn.execute("UPDATE auth_users SET password_reset_token_hash=%s,password_reset_expires_at=NOW()+INTERVAL '30 minutes',password_reset_required=TRUE WHERE id=%s AND status='active' RETURNING username,email",(self.token_hash(token),user_id)).fetchone()
            if not row:return None
            conn.execute("UPDATE auth_sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL",(user_id,));conn.commit()
        return {'reset_token':token,'username':row[0],'email':row[1]}

    def complete_password_reset(self, username: str, token: str, password: str, otp: str, ip: str | None=None) -> bool:
        self.validate_password(password);normalized=username.lower().strip()
        with self.connect() as conn:
            row=conn.execute("SELECT id,password_reset_token_hash,totp_secret FROM auth_users WHERE username=%s AND status='active' AND password_reset_required=TRUE AND password_reset_expires_at>NOW()",(normalized,)).fetchone()
            valid=bool(row and row[1] and hmac.compare_digest(self.token_hash(token),row[1]) and row[2] and pyotp.TOTP(row[2]).verify(otp,valid_window=1))
            if not valid:self.audit(normalized,'password_reset',False,ip);return False
            conn.execute("UPDATE auth_users SET password_hash=%s,password_reset_token_hash=NULL,password_reset_expires_at=NULL,password_reset_required=FALSE WHERE id=%s",(self.hash_password(password),row[0]))
            conn.execute("UPDATE auth_sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL",(row[0],));conn.commit()
        self.audit(normalized,'password_reset',True,ip,row[0]);return True

    def revoke_user_sessions(self, user_id: int) -> int:
        with self.connect() as conn:
            cur=conn.execute("UPDATE auth_sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL",(user_id,)); conn.commit(); return cur.rowcount

    def audit_entries(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows=conn.execute("SELECT username,action,success,ip_address,created_at FROM auth_audit_log ORDER BY created_at DESC LIMIT %s",(limit,)).fetchall()
        return [{'username':r[0],'action':r[1],'success':r[2],'ip_address':r[3],'created_at':r[4].isoformat()} for r in rows]


auth_service = AuthService()
