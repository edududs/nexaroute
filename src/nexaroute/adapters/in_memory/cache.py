from __future__ import annotations

import asyncio
from typing import Any

from nexaroute.core.ports.cache import CachePort


class InMemoryCacheAdapter(CachePort):
    def __init__(self) -> None:
        self._values: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        value = self._values.get(key)
        if value is None:
            return None
        stored, expires_at = value
        if expires_at is not None and expires_at <= asyncio.get_running_loop().time():
            self._values.pop(key, None)
            return None
        return stored

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = None if ttl is None else asyncio.get_running_loop().time() + ttl
        self._values[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._values.pop(key, None)
