from __future__ import annotations

from nexaroute.application.handlers import Handler


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        if name in self._handlers:
            raise ValueError(f"handler '{name}' already registered")
        self._handlers[name] = handler

    def resolve(self, name: str) -> Handler:
        try:
            return self._handlers[name]
        except KeyError as error:
            raise KeyError(f"handler '{name}' is not registered") from error
