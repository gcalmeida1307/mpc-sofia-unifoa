from __future__ import annotations

import asyncio

from context.infrastructure import snapshot_service
from services.knowledge import refresh_due_knowledge_sources
from learning.service import learning_service


class SnapshotScheduler:
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = max(5, int(interval_seconds))
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._running = True
        # Warm-up snapshot so temporal series starts immediately on boot.
        snapshot_service.refresh()
        refresh_due_knowledge_sources()
        learning_service.learn()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        while self._running:
            await asyncio.sleep(self.interval_seconds)
            snapshot_service.refresh()
            refresh_due_knowledge_sources()
            learning_service.learn()


snapshot_scheduler = SnapshotScheduler()
