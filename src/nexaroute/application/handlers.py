from __future__ import annotations

from collections.abc import Awaitable, Callable

from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import HandlerResult

type Handler = Callable[[ExecutionContext], Awaitable[HandlerResult]]
