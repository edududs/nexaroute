import pytest

from nexaroute.adapters.in_memory.cache import InMemoryCacheAdapter
from nexaroute.adapters.in_memory.state_store import InMemoryStateStoreAdapter
from nexaroute.application.registry import HandlerRegistry
from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.domain.results import CacheWrite, HandlerResult, LogEntry, StateWrite


class RecordingAction:
    def __init__(self) -> None:
        self.commands: list[OutboundCommand] = []

    def supports(self, command: OutboundCommand) -> bool:
        return command.target == "discord"

    async def execute(self, command: OutboundCommand) -> None:
        self.commands.append(command)


async def save_message(context: ExecutionContext) -> HandlerResult:
    return HandlerResult(
        commands=[OutboundCommand(name="notify", target="discord", payload={"message": "saved"})],
        state_writes=[StateWrite(namespace="messages", key="1", value={"saved": True})],
        cache_writes=[CacheWrite(key="latest", value={"id": "1"}, ttl=60)],
        logs=[LogEntry(level="info", message="saved")],
    )


@pytest.mark.asyncio
async def test_orchestrator_applies_handler_effects() -> None:
    from nexaroute.adapters.logging.rich_logger import RichLoggerAdapter
    from nexaroute.application.orchestrator import Orchestrator

    registry = HandlerRegistry()
    registry.register("message.received", save_message)
    action = RecordingAction()
    orchestrator = Orchestrator(
        handlers=registry,
        state_store=InMemoryStateStoreAdapter(),
        cache=InMemoryCacheAdapter(),
        logger=RichLoggerAdapter(),
        actions=[action],
    )

    event = InboundEvent(name="message.received", source="test", payload={})
    job = JobEnvelope.from_event(event)

    await orchestrator.process(job)

    assert await orchestrator.state_store.load("messages", "1") == {"saved": True}
    assert await orchestrator.cache.get("latest") == {"id": "1"}
    assert action.commands[0].name == "notify"
