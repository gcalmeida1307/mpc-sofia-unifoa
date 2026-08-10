from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


class AutonomyScheduler:
    def __init__(self, interval_seconds: int = 90):
        self.interval_seconds = max(20, int(interval_seconds))
        self._task: asyncio.Task | None = None
        self._running = False
        self._domain_jobs = []

    def configure_domain_jobs(self, jobs) -> None:
        self._domain_jobs = list(jobs)

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._running = True
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

    async def _run_cycle(self) -> None:
        try:
            for job in self._domain_jobs:
                await asyncio.to_thread(job)
        except Exception:
            logger.exception("SOFIA autonomous investigation cycle failed")

    async def _run(self) -> None:
        while self._running:
            await self._run_cycle()
            await asyncio.sleep(self.interval_seconds)


autonomy_scheduler = AutonomyScheduler()
