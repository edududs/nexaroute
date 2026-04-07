from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoggerPort(ABC):
    @abstractmethod
    async def debug(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def info(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def warning(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def error(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exception(self, message: str, **context: Any) -> None:
        raise NotImplementedError
