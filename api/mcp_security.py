"""Request-scoped authorization for the mounted streamable MCP adapter."""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any

from .auth import has_module_access, require_admin

_current_user: ContextVar[dict[str, Any] | None] = ContextVar("sofia_mcp_user", default=None)


def bind_user(user: dict[str, Any]) -> Token[dict[str, Any] | None]:
    return _current_user.set(user)


def reset_user(token: Token[dict[str, Any] | None]) -> None:
    _current_user.reset(token)


def current_user() -> dict[str, Any] | None:
    return _current_user.get()


def module_allowed(module_id: str) -> bool:
    user = current_user()
    return user is None or has_module_access(user, module_id)


def enforce_module(module_id: str) -> None:
    user = current_user()
    if user is not None and not has_module_access(user, module_id):
        raise PermissionError(f"Usuário sem acesso ao módulo {module_id}")


def enforce_admin() -> None:
    user = current_user()
    if user is not None:
        require_admin(user)

