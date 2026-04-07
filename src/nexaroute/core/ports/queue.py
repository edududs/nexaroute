from __future__ import annotations

from abc import ABC, abstractmethod

from nexaroute.core.domain.jobs import JobEnvelope


class QueuePort(ABC):
    @abstractmethod
    async def publish(self, job: JobEnvelope) -> None:
        raise NotImplementedError

    @abstractmethod
    async def consume(self) -> JobEnvelope:
        raise NotImplementedError

    @abstractmethod
    async def ack(self, job: JobEnvelope) -> None:
        raise NotImplementedError

    @abstractmethod
    async def nack(self, job: JobEnvelope, reason: str | None = None) -> None:
        raise NotImplementedError
