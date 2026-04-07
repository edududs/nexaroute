from __future__ import annotations

from abc import ABC, abstractmethod

from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.queue import QueuePort


class ExecutionProcessorPort(ABC):
    @abstractmethod
    async def process(self, job: JobEnvelope) -> None:
        raise NotImplementedError


class ExecutionStrategyPort(ABC):
    @abstractmethod
    async def start(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError
