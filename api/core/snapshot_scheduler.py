from __future__ import annotations

import asyncio
import logging

from learning.service import learning_service
from services.knowledge import refresh_due_knowledge_sources

logger = logging.getLogger(__name__)


class SnapshotScheduler:
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = max(5, int(interval_seconds))
        self._task: asyncio.Task | None = None
        self._running = False
        self._domain_jobs = []

    def configure_domain_jobs(self, jobs) -> None:
        self._domain_jobs = list(jobs)

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._running = True
        await self._run_cycle()
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

    def _refresh_learning_cycle(self) -> None:
        for job in self._domain_jobs:
            job()
        refresh_due_knowledge_sources()
        learning_service.learn()

    async def _run_cycle(self) -> None:
        try:
            await asyncio.to_thread(self._refresh_learning_cycle)
        except Exception:
            logger.exception("SOFIA snapshot, knowledge or learning cycle failed")

    async def _run(self) -> None:
        while self._running:
            await asyncio.sleep(self.interval_seconds)
            await self._run_cycle()


snapshot_scheduler = SnapshotScheduler()
