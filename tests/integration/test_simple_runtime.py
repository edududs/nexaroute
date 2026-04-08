import asyncio

import pytest

from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.results import HandlerResult, StateWrite
from nexaroute.core.ports.triggers import BaseTrigger, EventPublisher


class OneShotTrigger(BaseTrigger):
    def __init__(self) -> None:
        self._published = False

    async def start(self, publisher: EventPublisher) -> None:
        if self._published:
            return
        self._published = True
        await publisher(InboundEvent(name="message.received", source="trigger", payload={"text": "hello"}))

    async def stop(self) -> None:
        return None


async def persist_message(_: ExecutionContext) -> HandlerResult:
    return HandlerResult(
        state_writes=[StateWrite(namespace="messages", key="1", value={"text": "hello"})],
    )


@pytest.mark.asyncio
async def test_simple_runtime_processes_one_triggered_event() -> None:
    from nexaroute.application.bootstrap import create_simple_runtime

    runtime = create_simple_runtime(
        triggers=[OneShotTrigger()],
        handlers={"message.received": persist_message},
        concurrency=1,
    )

    await runtime.start()
    await asyncio.sleep(0.2)
    await runtime.stop()

    assert await runtime.orchestrator.state_store.load("messages", "1") == {"text": "hello"}
