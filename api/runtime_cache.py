"""Small process cache shared by the hot SOFIA read paths.

The durable document/index caches already live on disk. This layer avoids
repeating the expensive ranking and judge work for the same question while a
worker is alive. Keys contain only normalized request metadata and corpus
stamps; cached values are never logged or serialized to a client.
"""

from __future__ import annotations

import os
import threading
from collections import OrderedDict
from collections.abc import Hashable
from typing import Any


def _max_entries() -> int:
    try:
        return max(16, min(512, int(os.getenv("SOFIA_RETRIEVAL_CACHE_ENTRIES", "128"))))
    except ValueError:
        return 128


_CACHE: OrderedDict[tuple[str, Hashable], Any] = OrderedDict()
_LOCK = threading.RLock()
_HITS = 0
_MISSES = 0


def get(namespace: str, key: Hashable) -> Any | None:
    global _HITS, _MISSES
    with _LOCK:
        cache_key = (namespace, key)
        if cache_key not in _CACHE:
            _MISSES += 1
            return None
        _HITS += 1
        value = _CACHE.pop(cache_key)
        _CACHE[cache_key] = value
        return value


def set(namespace: str, key: Hashable, value: Any) -> None:
    with _LOCK:
        cache_key = (namespace, key)
        _CACHE.pop(cache_key, None)
        _CACHE[cache_key] = value
        while len(_CACHE) > _max_entries():
            _CACHE.popitem(last=False)


def clear(namespace: str | None = None) -> None:
    with _LOCK:
        if namespace is None:
            _CACHE.clear()
        else:
            for key in tuple(_CACHE):
                if key[0] == namespace:
                    _CACHE.pop(key, None)


def stats() -> dict[str, int]:
    with _LOCK:
        return {"entries": len(_CACHE), "hits": _HITS, "misses": _MISSES}
