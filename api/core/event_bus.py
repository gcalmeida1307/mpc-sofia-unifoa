from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable

EventHandler = Callable[[dict[str, Any]], Any | Awaitable[Any]]


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        self._subscribers[topic].append(handler)

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            result = handler(payload)
            if asyncio.iscoroutine(result):
                await result

    def publish_sync(self, topic: str, payload: dict[str, Any]) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(topic, payload))
        except RuntimeError:
            asyncio.run(self.publish(topic, payload))

    def subscribers_count(self, topic: str) -> int:
        return len(self._subscribers.get(topic, []))

    def snapshot(self) -> dict[str, int]:
        return {topic: len(handlers) for topic, handlers in self._subscribers.items()}

    def clear(self) -> None:
        self._subscribers.clear()


event_bus = EventBus()
