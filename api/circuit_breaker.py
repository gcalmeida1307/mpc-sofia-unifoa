"""Small in-process circuit breakers for model providers.

The breaker is intentionally provider-scoped and process-local. It protects
the local API from a failing remote dependency; it is not a replacement for a
distributed gateway breaker in a multi-worker deployment.
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Any


def _positive_int(name: str, default: int, maximum: int = 100) -> int:
    try:
        return max(1, min(maximum, int(os.getenv(name, str(default)))))
    except ValueError:
        return default


def _positive_float(name: str, default: float, maximum: float = 3600.0) -> float:
    try:
        return max(0.1, min(maximum, float(os.getenv(name, str(default)))))
    except ValueError:
        return default


@dataclass
class _State:
    failures: int = 0
    opened_at: float = 0.0
    half_open: bool = False


class ProviderCircuitBreaker:
    def __init__(self) -> None:
        self._states: dict[str, _State] = {}
        self._lock = threading.RLock()

    @property
    def failure_threshold(self) -> int:
        return _positive_int("SOFIA_PROVIDER_FAILURE_THRESHOLD", 3, 20)

    @property
    def recovery_seconds(self) -> float:
        return _positive_float("SOFIA_PROVIDER_RECOVERY_SECONDS", 60.0)

    def allow(self, provider: str) -> bool:
        now = time.monotonic()
        with self._lock:
            state = self._states.get(provider)
            if state is None or state.opened_at <= 0:
                return True
            if now - state.opened_at >= self.recovery_seconds:
                state.half_open = True
                return True
            return False

    def success(self, provider: str) -> None:
        with self._lock:
            self._states.pop(provider, None)

    def failure(self, provider: str) -> None:
        with self._lock:
            state = self._states.setdefault(provider, _State())
            state.failures += 1
            if state.failures >= self.failure_threshold or state.half_open:
                state.opened_at = time.monotonic()
                state.half_open = False

    def reset(self, provider: str | None = None) -> None:
        with self._lock:
            if provider is None:
                self._states.clear()
            else:
                self._states.pop(provider, None)

    def status(self) -> dict[str, Any]:
        now = time.monotonic()
        with self._lock:
            providers = {}
            for provider, state in self._states.items():
                is_open = state.opened_at > 0 and now - state.opened_at < self.recovery_seconds
                providers[provider] = {
                    "state": "open" if is_open else ("half_open" if state.opened_at else "closed"),
                    "failures": state.failures,
                    "retry_in_seconds": round(max(0.0, self.recovery_seconds - (now - state.opened_at)), 2) if is_open else 0.0,
                }
            return {
                "failure_threshold": self.failure_threshold,
                "recovery_seconds": self.recovery_seconds,
                "providers": providers,
            }


PROVIDER_BREAKER = ProviderCircuitBreaker()


def circuit_status() -> dict[str, Any]:
    return PROVIDER_BREAKER.status()


__all__ = ["PROVIDER_BREAKER", "ProviderCircuitBreaker", "circuit_status"]

