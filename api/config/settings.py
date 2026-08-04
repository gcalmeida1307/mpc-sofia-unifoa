from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str


@dataclass(frozen=True)
class ZabbixConfig:
    url: str | None
    user: str | None
    password: str | None


@dataclass(frozen=True)
class PostgresConfig:
    dsn: str


@dataclass(frozen=True)
class QdrantConfig:
    url: str
    collection: str


@dataclass(frozen=True)
class N8NConfig:
    base_url: str
    default_webhook: str


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str
    model: str
    fallback_model: str
    api_key: str
    mode: str


@dataclass(frozen=True)
class RuntimeConfig:
    request_timeout: int
    debug: bool
    snapshot_interval_seconds: int
    autonomous_investigation_interval_seconds: int
    ai_metrics_window_hours: int
    request_rate_limit_per_minute: int


@dataclass(frozen=True)
class SecurityConfig:
    admin_api_key: str
    mfa_totp_secret: str


class Settings:
    def __init__(self):
        self.openai = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
        )
        self.zabbix = ZabbixConfig(
            url=os.getenv("ZABBIX_URL"),
            user=os.getenv("ZABBIX_USER"),
            password=os.getenv("ZABBIX_PASSWORD"),
        )
        self.postgres = PostgresConfig(
            dsn=os.getenv("POSTGRES_DSN", "postgresql://sofia:sofia123@sofia_postgres:5432/sofia"),
        )
        self.qdrant = QdrantConfig(
            url=os.getenv("QDRANT_URL", "http://sofia_qdrant:6333"),
            collection=os.getenv("QDRANT_COLLECTION", "sofia_memory"),
        )
        self.n8n = N8NConfig(
            base_url=os.getenv("N8N_BASE_URL", "http://sofia_n8n:5678"),
            default_webhook=os.getenv("N8N_DEFAULT_WEBHOOK", "sofia-investigation"),
        )
        self.ollama = OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
            fallback_model=os.getenv("OLLAMA_FALLBACK_MODEL", ""),
            api_key=os.getenv("OLLAMA_API_KEY", ""),
            mode=os.getenv("OLLAMA_MODE", "native").strip().lower() or "native",
        )
        self.runtime = RuntimeConfig(
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            debug=_as_bool(os.getenv("DEBUG"), default=False),
            snapshot_interval_seconds=int(os.getenv("SNAPSHOT_INTERVAL_SECONDS", "30")),
            autonomous_investigation_interval_seconds=int(os.getenv("AUTONOMOUS_INVESTIGATION_INTERVAL_SECONDS", "90")),
            ai_metrics_window_hours=int(os.getenv("AI_METRICS_WINDOW_HOURS", "24")),
            request_rate_limit_per_minute=int(os.getenv("REQUEST_RATE_LIMIT_PER_MINUTE", "120")),
        )
        self.security = SecurityConfig(
            admin_api_key=os.getenv("SECURITY_ADMIN_API_KEY", ""),
            mfa_totp_secret=os.getenv("SECURITY_MFA_TOTP_SECRET", ""),
        )

        # Backward-compatible attributes used across existing services.
        self.ZABBIX_URL = self.zabbix.url
        self.ZABBIX_USER = self.zabbix.user
        self.ZABBIX_PASSWORD = self.zabbix.password
        self.REQUEST_TIMEOUT = self.runtime.request_timeout
        self.SNAPSHOT_INTERVAL_SECONDS = self.runtime.snapshot_interval_seconds
        self.AUTONOMOUS_INVESTIGATION_INTERVAL_SECONDS = self.runtime.autonomous_investigation_interval_seconds
        self.AI_METRICS_WINDOW_HOURS = self.runtime.ai_metrics_window_hours
        self.REQUEST_RATE_LIMIT_PER_MINUTE = self.runtime.request_rate_limit_per_minute
        self.SECURITY_ADMIN_API_KEY = self.security.admin_api_key
        self.SECURITY_MFA_TOTP_SECRET = self.security.mfa_totp_secret
        self.POSTGRES_DSN = self.postgres.dsn
        self.QDRANT_URL = self.qdrant.url
        self.QDRANT_COLLECTION = self.qdrant.collection
        self.N8N_BASE_URL = self.n8n.base_url
        self.N8N_DEFAULT_WEBHOOK = self.n8n.default_webhook
        self.OPENAI_API_KEY = self.openai.api_key
        self.OPENAI_MODEL = self.openai.model
        self.OLLAMA_BASE_URL = self.ollama.base_url
        self.OLLAMA_MODEL = self.ollama.model
        self.OLLAMA_FALLBACK_MODEL = self.ollama.fallback_model
        self.OLLAMA_API_KEY = self.ollama.api_key
        self.OLLAMA_MODE = self.ollama.mode

    @staticmethod
    def _mask(value: str | None) -> str:
        if not value:
            return ""
        if len(value) <= 6:
            return "***"
        return f"{value[:3]}***{value[-2:]}"

    def snapshot(self, masked: bool = True) -> dict[str, object]:
        openai_api_key = self._mask(self.openai.api_key) if masked else self.openai.api_key
        ollama_api_key = self._mask(self.ollama.api_key) if masked else self.ollama.api_key
        zabbix_password = self._mask(self.zabbix.password) if masked else self.zabbix.password
        return {
            "openai": {
                "api_key": openai_api_key,
                "model": self.openai.model,
            },
            "zabbix": {
                "url": self.zabbix.url,
                "user": self.zabbix.user,
                "password": zabbix_password,
            },
            "postgres": {"dsn": self._mask(self.postgres.dsn) if masked else self.postgres.dsn},
            "qdrant": {
                "url": self.qdrant.url,
                "collection": self.qdrant.collection,
            },
            "n8n": {
                "base_url": self.n8n.base_url,
                "default_webhook": self.n8n.default_webhook,
            },
            "ollama": {
                "base_url": self.ollama.base_url,
                "model": self.ollama.model,
                "fallback_model": self.ollama.fallback_model,
                "api_key": ollama_api_key,
                "mode": self.ollama.mode,
            },
            "security": {
                "admin_api_key": self._mask(self.security.admin_api_key) if masked else self.security.admin_api_key,
                "mfa_totp_secret": self._mask(self.security.mfa_totp_secret) if masked else self.security.mfa_totp_secret,
            },
            "runtime": {
                "request_timeout": self.runtime.request_timeout,
                "debug": self.runtime.debug,
                "snapshot_interval_seconds": self.runtime.snapshot_interval_seconds,
                "autonomous_investigation_interval_seconds": self.runtime.autonomous_investigation_interval_seconds,
                "ai_metrics_window_hours": self.runtime.ai_metrics_window_hours,
                "request_rate_limit_per_minute": self.runtime.request_rate_limit_per_minute,
            },
        }


settings = Settings()
