from __future__ import annotations

import os
import re
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .pg_runtime import is_postgres, postgres_connection
from .secure_storage import encryption_configured

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "sofia.sqlite3"
PG_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    user_code TEXT NOT NULL,
    module_id TEXT,
    action TEXT NOT NULL,
    resource_id TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_events_created ON audit_events (created_at DESC);
CREATE TABLE IF NOT EXISTS privacy_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


@contextmanager
def _connection() -> Iterator[object]:
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


# These masks are deliberately request-scoped. The mapping is kept only in
# memory until the provider answer has been rehydrated, and is never written to
# analytics, audit logs, learning events or the offline knowledge base.
_PLACEHOLDER_RE = re.compile(
    r"__SOFIA_(?:EMAIL|CPF|CNPJ|PHONE|IP|UUID|IDENTIFIER|PII)_\d+__"
)
_SECRET_RE = re.compile(
    r"(?ix)"
    r"(?:bearer\s+[A-Za-z0-9._~+/=-]{16,}|"
    r"sk-(?:proj|live|test)-[A-Za-z0-9._-]{12,}|"
    r"AIza[0-9A-Za-z_-]{20,}|"
    r"(?:api[_ -]?key|secret|token|senha|password)\s*[:=]\s*[^\s,;]+)"
)
_KEYED_PII_RE = re.compile(
    r"(?P<prefix>(?:[\"']?(?:patient[_ -]?id|patientId|user[_ -]?id|userId|account[_ -]?id|"
    r"identifier|name|given|family|birth[_ -]?date|birthDate|email|phone|telephone|telecom|"
    r"address|postal[_ -]?code|postalCode|cpf|cnpj|document|documento|matricula|matrícula))"
    r"[\"']?\s*[:=]\s*)"
    r"(?P<value>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|\[[^\]]*\]|[^,\n}]+)",
    re.IGNORECASE,
)
_FHIR_IDENTIFIER_RE = re.compile(
    r"(?P<prefix>[\"']?(?:id|resourceId|reference|fullUrl)[\"']?\s*[:=]\s*)"
    r"(?P<value>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|[^,\n}]+)",
    re.IGNORECASE,
)
_EMAIL_RE = re.compile(
    r"(?<![\w.+-])[\w.!#$%&'*+/=?^`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}(?![\w-])"
)
_CNPJ_RE = re.compile(r"(?<!\d)\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2}(?!\d)")
_CPF_RE = re.compile(r"(?<!\d)\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}(?!\d)")
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?55[\s.-]?)?(?:\(?\d{2}\)?[\s.-]?)9?\d{4}[\s.-]?\d{4}(?!\d)"
)
_IP_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w])")
_UUID_RE = re.compile(
    r"(?<![\w-])[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}(?![\w-])",
    re.IGNORECASE,
)


class ExternalRedaction:
    """Mask direct identifiers before a cloud request and restore only tokens.

    This is not a substitute for LGPD governance or a data-classification
    system. It is a technical minimization layer: a provider can help rewrite
    an answer using anonymized context, but it cannot receive the original
    identifier. Secrets are removed without a restore mapping by design.
    """

    def __init__(self) -> None:
        self._restore_map: dict[str, str] = {}
        self._counters: dict[str, int] = {}
        self._masked_fields = 0

    @property
    def masked_fields(self) -> int:
        return self._masked_fields

    @property
    def used(self) -> bool:
        return self._masked_fields > 0

    def _placeholder(self, kind: str, value: str, *, restorable: bool = True) -> str:
        if not value:
            return value
        if restorable:
            # Reusing the same marker makes repeated values (for example a
            # patient email in the question and history) consistent to the LLM.
            for token, original in self._restore_map.items():
                if original == value:
                    return token
        self._counters[kind] = self._counters.get(kind, 0) + 1
        token = f"__SOFIA_{kind}_{self._counters[kind]}__"
        if restorable:
            self._restore_map[token] = value
        self._masked_fields += 1
        return token

    def _replace_secret(self, match: re.Match[str]) -> str:
        self._masked_fields += 1
        return "[SEGREDO_REMOVIDO]"

    def _replace_keyed(self, match: re.Match[str]) -> str:
        key = match.group("prefix")
        value = match.group("value").strip()
        # Preserve JSON-ish quoting so the anonymized FHIR context remains
        # understandable to a provider without exposing the original value.
        quoted = len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}
        kind = "PII"
        lowered = key.casefold()
        if "email" in lowered:
            kind = "EMAIL"
        elif "cpf" in lowered:
            kind = "CPF"
        elif "cnpj" in lowered:
            kind = "CNPJ"
        elif "phone" in lowered or "telephone" in lowered or "telecom" in lowered:
            kind = "PHONE"
        elif "birth" in lowered:
            kind = "PII"
        token = self._placeholder(kind, value[1:-1] if quoted else value)
        return f"{key}{value[0]}{token}{value[-1]}" if quoted else f"{key}{token}"

    def _replace_pattern(self, kind: str) -> Callable[[re.Match[str]], str]:
        def replace(match: re.Match[str]) -> str:
            return self._placeholder(kind, match.group(0))

        return replace

    def clean(self, text: str | None) -> str:
        """Return text safe to send to an external provider for this request."""
        if not text:
            return ""
        cleaned = _SECRET_RE.sub(self._replace_secret, str(text))
        cleaned = _KEYED_PII_RE.sub(self._replace_keyed, cleaned)
        # Do not process already-issued markers. They are intentionally stable
        # across prompt sections and can be restored after generation.
        protected: dict[str, str] = {}

        def protect(match: re.Match[str]) -> str:
            key = f"__SOFIA_PROTECTED_{len(protected) + 1}__"
            protected[key] = match.group(0)
            return key

        cleaned = _PLACEHOLDER_RE.sub(protect, cleaned)
        for kind, pattern in (
            ("EMAIL", _EMAIL_RE),
            ("CNPJ", _CNPJ_RE),
            ("CPF", _CPF_RE),
            ("PHONE", _PHONE_RE),
            ("IP", _IP_RE),
            ("UUID", _UUID_RE),
        ):
            cleaned = pattern.sub(self._replace_pattern(kind), cleaned)
        for marker, original in protected.items():
            cleaned = cleaned.replace(marker, original)
        return cleaned

    def clean_history(self, history: list[dict[str, str]]) -> list[dict[str, str]]:
        return [
            {**item, "content": self.clean(str(item.get("content", "")))}
            for item in history
            if item.get("role") in {"user", "assistant"}
            and str(item.get("content", "")).strip()
        ]

    def clean_clinical(self, text: str | None) -> str:
        """Apply the normal minimization plus the FHIR identifier boundary.

        Generic FHIR ``id`` and ``reference`` fields are not always covered by
        the natural-language PII patterns.  They are therefore replaced only
        on the clinical context path, while the local RAG keeps the original
        resource for authorized processing.
        """

        cleaned = self.clean(text)

        def replace(match: re.Match[str]) -> str:
            key = match.group("prefix")
            value = match.group("value").strip()
            quoted = len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}
            token = self._placeholder("IDENTIFIER", value[1:-1] if quoted else value)
            return f"{key}{value[0]}{token}{value[-1]}" if quoted else f"{key}{token}"

        return _FHIR_IDENTIFIER_RE.sub(replace, cleaned)

    def restore(self, text: str | None) -> str:
        if not text or not self._restore_map:
            return text or ""
        restored = str(text)
        # Longer values first avoids accidental prefix collisions if a future
        # placeholder family is introduced.
        for token, original in sorted(
            self._restore_map.items(), key=lambda item: len(item[0]), reverse=True
        ):
            restored = restored.replace(token, original)
        return restored


def external_generation_may_be_used(provider: str, allowed: bool | None = None) -> bool:
    """Whether the selected route can reach OpenAI, Gemini or Claude."""
    permitted = external_data_allowed() if allowed is None else bool(allowed)
    return permitted and provider in {"auto", "openai", "gemini", "claude"}


def _enabled(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on", "sim"}


def external_data_allowed() -> bool:
    """External providers require an explicit opt-in in the local deployment."""
    return _enabled("SOFIA_ALLOW_EXTERNAL_DATA", False)


def external_clinical_allowed() -> bool:
    return external_data_allowed() and _enabled("SOFIA_ALLOW_EXTERNAL_CLINICAL", False)


def provider_guard(
    provider: str, *, patient_id: str | None = None, clinical: bool = False
) -> None:
    if provider not in {"gemini", "claude", "openai"}:
        return
    if not external_data_allowed():
        raise ValueError(
            "Provider externo bloqueado pelo modo LGPD local. Use Ollama ou habilite SOFIA_ALLOW_EXTERNAL_DATA após avaliar a finalidade e a base legal."
        )
    if (patient_id or clinical) and not external_clinical_allowed():
        raise ValueError(
            "Contexto FHIR/paciente não é enviado a providers externos por padrão. Use Ollama local ou habilite SOFIA_ALLOW_EXTERNAL_CLINICAL de forma explícita."
        )


def initialize_privacy_store() -> None:
    with _connection() as connection:
        if is_postgres(connection):
            connection.executescript(PG_SCHEMA)
        else:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_code TEXT NOT NULL,
                    module_id TEXT,
                    action TEXT NOT NULL,
                    resource_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
        cutoff = (datetime.now(UTC) - timedelta(days=retention_days())).isoformat()
        connection.execute("DELETE FROM audit_events WHERE created_at < ?", (cutoff,))
        connection.commit()


def retention_days() -> int:
    try:
        return max(1, min(3_650, int(os.getenv("SOFIA_AUDIT_RETENTION_DAYS", "365"))))
    except ValueError:
        return 365


def audit_event(
    user_code: str,
    action: str,
    module_id: str | None = None,
    resource_id: str | None = None,
) -> None:
    """Record metadata only; prompts, documents and clinical values are never written here."""
    try:
        with _connection() as connection:
            connection.execute(
                "INSERT INTO audit_events (user_code, module_id, action, resource_id, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    user_code,
                    module_id,
                    action,
                    resource_id,
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.commit()
    except (sqlite3.Error, RuntimeError):
        # Audit failure must not turn a successful local operation into data loss.
        return


def status() -> dict[str, object]:
    return {
        "mode": "local-first",
        "external_data_allowed": external_data_allowed(),
        "external_clinical_allowed": external_clinical_allowed(),
        "audit_log": True,
        "audit_retention_days": retention_days(),
        "data_minimization": True,
        "external_redaction": True,
        "encryption_at_rest": encryption_configured(),
        "storage": "postgresql:sofia_runtime"
        if postgres_dsn_configured()
        else "sqlite",
        "redaction_scope": "por requisição; identificadores diretos são mascarados e segredos não são restaurados",
        "fhir_external_default": "blocked",
        "note": "Controles técnicos de privacidade; a adequação jurídica depende da finalidade, base legal, governança e operação do responsável.",
    }


def postgres_dsn_configured() -> bool:
    return bool(os.getenv("SOFIA_POSTGRES_URL", os.getenv("DATABASE_URL", "")).strip())
