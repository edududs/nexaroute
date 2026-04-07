from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope

EventPublisher = Callable[[InboundEvent], Awaitable[JobEnvelope]]


class BaseTrigger(ABC):
    @abstractmethod
    async def start(self, publisher: EventPublisher) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError
