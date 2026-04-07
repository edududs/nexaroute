from __future__ import annotations

import asyncio

from nexaroute.core.ports.execution import ExecutionProcessorPort, ExecutionStrategyPort
from nexaroute.core.ports.queue import QueuePort


class InMemoryExecutionAdapter(ExecutionStrategyPort):
    def __init__(self, concurrency: int = 1, poll_interval: float = 0.05) -> None:
        self._concurrency = concurrency
        self._poll_interval = poll_interval
        self._stop_event = asyncio.Event()
        self._supervisor: asyncio.Task[None] | None = None

    async def start(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        if self._supervisor is not None:
            raise RuntimeError("execution strategy already started")
        self._stop_event.clear()
        self._supervisor = asyncio.create_task(self._run(queue, processor))

    async def stop(self) -> None:
        if self._supervisor is None:
            return
        self._stop_event.set()
        await self._supervisor
        self._supervisor = None

    async def _run(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        async with asyncio.TaskGroup() as group:
            for _ in range(self._concurrency):
                group.create_task(self._consume(queue, processor))

    async def _consume(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        while not self._stop_event.is_set():
            try:
                async with asyncio.timeout(self._poll_interval):
                    job = await queue.consume()
            except TimeoutError:
                continue

            try:
                await processor.process(job)
            except Exception as error:
                await queue.nack(job, reason=str(error))
                continue

            await queue.ack(job)
