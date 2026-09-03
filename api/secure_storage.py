"""Application-level encryption for sensitive values stored by SOFIA.

The database must still use disk encryption and TLS in production.  This
module adds a second, application-level boundary for payloads that contain
health, identity or institutional data.  Legacy plaintext values remain
readable so an operator can migrate them without data loss.
"""

from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

PREFIX = "sofia:v1:"


def _fernet() -> Fernet | None:
    configured = os.getenv(
        "SOFIA_ENCRYPTION_KEY", os.getenv("SOFIA_DATA_ENCRYPTION_KEY", "")
    ).strip()
    if not configured:
        return None
    try:
        key = configured.encode("ascii")
        Fernet(key)
    except (ValueError, TypeError, UnicodeEncodeError):
        # Accept a high-entropy secret from a secret manager even when it is
        # not already in Fernet's URL-safe base64 representation.
        key = base64.urlsafe_b64encode(hashlib.sha256(configured.encode()).digest())
    return Fernet(key)


def encryption_configured() -> bool:
    return _fernet() is not None


def encrypt_text(value: str | None) -> str | None:
    if value is None or value.startswith(PREFIX):
        return value
    cipher = _fernet()
    if cipher is None:
        raise RuntimeError(
            "SOFIA_ENCRYPTION_KEY não configurada para proteger dados sensíveis"
        )
    return PREFIX + cipher.encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_text(value: str | None) -> str:
    if not value:
        return ""
    if not value.startswith(PREFIX):
        return value
    cipher = _fernet()
    if cipher is None:
        raise RuntimeError("SOFIA_ENCRYPTION_KEY necessária para ler dados protegidos")
    try:
        return cipher.decrypt(value[len(PREFIX) :].encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError("valor protegido não pôde ser descriptografado") from exc


def encrypt_json(value: str | None) -> str | None:
    return encrypt_text(value)


def decrypt_json(value: str | None) -> str:
    return decrypt_text(value)


def protect_for_storage(value: str | None) -> str | None:
    """Encrypt in every configured deployment; allow plaintext only in dev."""
    if encryption_configured():
        return encrypt_text(value)
    if os.getenv("SOFIA_STORAGE_MODE", "developer").strip().casefold() in {
        "production",
        "strict",
        "primary",
    }:
        raise RuntimeError(
            "SOFIA_ENCRYPTION_KEY não configurada para armazenamento de produção"
        )
    return value
