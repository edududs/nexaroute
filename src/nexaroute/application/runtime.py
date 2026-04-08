from __future__ import annotations

from collections.abc import Sequence

from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.execution import ExecutionStrategyPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.queue import QueuePort
from nexaroute.core.ports.triggers import BaseTrigger


class DispatcherRuntime:
    def __init__(
        self,
        *,
        queue: QueuePort,
        execution: ExecutionStrategyPort,
        orchestrator,
        triggers: Sequence[BaseTrigger],
        logger: LoggerPort,
    ) -> None:
        self.queue = queue
        self.execution = execution
        self.orchestrator = orchestrator
        self.triggers = list(triggers)
        self.logger = logger
        self._started = False

    async def publish_event(self, event: InboundEvent) -> JobEnvelope:
        job = JobEnvelope.from_event(event)
        await self.queue.publish(job)
        await self.logger.debug("event dispatched", event_name=event.name, job_id=job.job_id)
        return job

    async def start(self) -> None:
        if self._started:
            return
        await self.execution.start(self.queue, self.orchestrator)
        for trigger in self.triggers:
            await trigger.start(self.publish_event)
        self._started = True
        await self.logger.info("runtime started", trigger_count=len(self.triggers))

    async def stop(self) -> None:
        if not self._started:
            return
        for trigger in self.triggers:
            await trigger.stop()
        await self.execution.stop()
        self._started = False
        await self.logger.info("runtime stopped")
