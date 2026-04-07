from datetime import UTC, datetime

from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.domain.results import CacheWrite, HandlerResult, LogEntry, StateWrite


def test_inbound_event_defaults() -> None:
    event = InboundEvent(name="message.received", source="test", payload={"text": "hi"})

    assert event.handler_name is None
    assert event.correlation_id == event.id
    assert event.occurred_at.tzinfo is UTC


def test_job_envelope_uses_event_correlation() -> None:
    event = InboundEvent(name="message.received", source="test", payload={})

    job = JobEnvelope.from_event(event)

    assert job.event == event
    assert job.handler_name is None
    assert job.correlation_id == event.correlation_id
    assert job.attempt == 1


def test_handler_result_defaults_to_empty_effects() -> None:
    result = HandlerResult()

    assert result.commands == []
    assert result.state_writes == []
    assert result.cache_writes == []
    assert result.logs == []


def test_handler_result_accepts_structured_effects() -> None:
    now = datetime.now(UTC)
    command = OutboundCommand(name="notify", target="discord", payload={"message": "done"})

    result = HandlerResult(
        commands=[command],
        state_writes=[StateWrite(namespace="messages", key="1", value={"saved": True})],
        cache_writes=[CacheWrite(key="latest", value={"id": "1"}, ttl=60)],
        logs=[LogEntry(level="info", message="processed", timestamp=now, context={"event": "message.received"})],
    )

    assert result.commands[0].target == "discord"
    assert result.state_writes[0].namespace == "messages"
    assert result.cache_writes[0].ttl == 60
    assert result.logs[0].level == "info"
