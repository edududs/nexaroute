from __future__ import annotations

from abc import ABC, abstractmethod

from nexaroute.core.domain.commands import OutboundCommand


class BaseAction(ABC):
    @abstractmethod
    def supports(self, command: OutboundCommand) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, command: OutboundCommand) -> None:
        raise NotImplementedError
