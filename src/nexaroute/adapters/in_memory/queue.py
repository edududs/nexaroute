from __future__ import annotations

import asyncio

from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.queue import QueuePort


class InMemoryQueueAdapter(QueuePort):
    def __init__(self) -> None:
        self._queue: asyncio.Queue[JobEnvelope] = asyncio.Queue()
        self._inflight: dict[str, JobEnvelope] = {}
        self._nacked: dict[str, str | None] = {}

    async def publish(self, job: JobEnvelope) -> None:
        await self._queue.put(job)

    async def consume(self) -> JobEnvelope:
        job = await self._queue.get()
        self._inflight[job.job_id] = job
        return job

    async def ack(self, job: JobEnvelope) -> None:
        self._inflight.pop(job.job_id, None)

    async def nack(self, job: JobEnvelope, reason: str | None = None) -> None:
        self._inflight.pop(job.job_id, None)
        self._nacked[job.job_id] = reason
