from __future__ import annotations

from copy import deepcopy
from typing import Any

from nexaroute.core.ports.state_store import StateStorePort


class InMemoryStateStoreAdapter(StateStorePort):
    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = {}

    async def load(self, namespace: str, key: str) -> dict[str, Any] | None:
        value = self._data.get(namespace, {}).get(key)
        return deepcopy(value) if value is not None else None

    async def save(self, namespace: str, key: str, value: dict[str, Any]) -> None:
        self._data.setdefault(namespace, {})[key] = deepcopy(value)

    async def delete(self, namespace: str, key: str) -> None:
        namespace_data = self._data.get(namespace)
        if namespace_data is None:
            return
        namespace_data.pop(key, None)
