from __future__ import annotations

import time

from services.postgres_store import postgres_store


class PlannerPolicy:
    def __init__(self, cache_ttl_seconds: int = 60):
        self.cache_ttl_seconds = max(5, int(cache_ttl_seconds))
        self._cache: dict[str, dict] = {}
        self._last_refresh = 0.0

    def weights(self) -> dict[str, dict]:
        now = time.time()
        if self._cache and (now - self._last_refresh) < self.cache_ttl_seconds:
            return self._cache
        self._cache = postgres_store.get_planner_policy_weights()
        self._last_refresh = now
        return self._cache

    def rank_capabilities(self, capabilities: list[str]) -> list[str]:
        if len(capabilities) <= 1:
            return capabilities
        weighted = self.weights()
        return sorted(
            capabilities,
            key=lambda capability: float(weighted.get(capability, {}).get("weight", 1.0)),
            reverse=True,
        )

    def feedback(self, capabilities: list[str], success: bool, confidence: float) -> None:
        delta = float(confidence) - 0.5
        for capability in capabilities:
            postgres_store.update_planner_policy(
                capability=capability,
                success=success,
                confidence_delta=delta,
            )
        # Force refresh on next read.
        self._last_refresh = 0.0


planner_policy = PlannerPolicy()
