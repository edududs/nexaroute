from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StateStorePort(ABC):
    @abstractmethod
    async def load(self, namespace: str, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, namespace: str, key: str, value: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, namespace: str, key: str) -> None:
        raise NotImplementedError
