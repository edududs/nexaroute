from __future__ import annotations

from collections.abc import Mapping, Sequence

from nexaroute.adapters.in_memory.cache import InMemoryCacheAdapter
from nexaroute.adapters.in_memory.execution import InMemoryExecutionAdapter
from nexaroute.adapters.in_memory.queue import InMemoryQueueAdapter
from nexaroute.adapters.in_memory.state_store import InMemoryStateStoreAdapter
from nexaroute.adapters.logging.rich_logger import RichLoggerAdapter
from nexaroute.application.handlers import Handler
from nexaroute.application.orchestrator import Orchestrator
from nexaroute.application.registry import HandlerRegistry
from nexaroute.application.runtime import DispatcherRuntime
from nexaroute.core.ports.actions import BaseAction
from nexaroute.core.ports.triggers import BaseTrigger


def create_simple_runtime(
    *,
    triggers: Sequence[BaseTrigger],
    handlers: Mapping[str, Handler],
    actions: Sequence[BaseAction] = (),
    concurrency: int = 1,
) -> DispatcherRuntime:
    registry = HandlerRegistry()
    for name, handler in handlers.items():
        registry.register(name, handler)

    logger = RichLoggerAdapter()
    orchestrator = Orchestrator(
        handlers=registry,
        state_store=InMemoryStateStoreAdapter(),
        cache=InMemoryCacheAdapter(),
        logger=logger,
        actions=list(actions),
    )
    return DispatcherRuntime(
        queue=InMemoryQueueAdapter(),
        execution=InMemoryExecutionAdapter(concurrency=concurrency),
        orchestrator=orchestrator,
        triggers=triggers,
        logger=logger,
    )
