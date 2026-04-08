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
        self._execution_started = False
        self._started_triggers: list[BaseTrigger] = []

    async def publish_event(self, event: InboundEvent) -> JobEnvelope:
        job = JobEnvelope.from_event(event)
        await self.queue.publish(job)
        await self.logger.debug("event dispatched", event_name=event.name, job_id=job.job_id)
        return job

    async def start(self) -> None:
        if self._started:
            return

        await self.execution.start(self.queue, self.orchestrator)
        self._execution_started = True

        try:
            for trigger in self.triggers:
                self._started_triggers.append(trigger)
                await trigger.start(self.publish_event)
        except Exception as exc:
            try:
                await self._stop_started_components()
            except Exception as cleanup_exc:
                raise cleanup_exc from exc
            raise

        self._started = True
        await self.logger.info("runtime started", trigger_count=len(self.triggers))

    async def stop(self) -> None:
        if not self._started and not self._execution_started:
            return

        try:
            await self._stop_started_components()
        finally:
            self._started = False

        await self.logger.info("runtime stopped")

    async def _stop_started_components(self) -> None:
        first_error: Exception | None = None

        while self._started_triggers:
            trigger = self._started_triggers.pop()
            try:
                await trigger.stop()
            except Exception as exc:
                if first_error is None:
                    first_error = exc

        if self._execution_started:
            self._execution_started = False
            try:
                await self.execution.stop()
            except Exception as exc:
                if first_error is None:
                    first_error = exc

        self._started = False

        if first_error is not None:
            raise first_error
