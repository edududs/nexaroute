from collections.abc import Mapping
from datetime import UTC, datetime

import pytest

from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.context import ExecutionContext
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
    assert job.causation_id == event.id
    assert job.attempt == 1


def test_value_objects_expose_immutable_collection_shapes() -> None:
    event = InboundEvent(name="message.received", source="test", payload={"text": "hi"}, metadata={"source": "unit"})
    command = OutboundCommand(name="notify", target="discord", payload={"message": "done"}, metadata={"priority": "high"})
    job = JobEnvelope(event=event, correlation_id=event.correlation_id, metadata={"queue": "default"})
    result = HandlerResult(
        commands=[command],
        state_writes=[StateWrite(namespace="messages", key="1", value={"saved": True})],
        cache_writes=[CacheWrite(key="latest", value={"id": "1"}, ttl=60)],
        logs=[LogEntry(level="info", message="processed", context={"event": "message.received"})],
    )
    context = ExecutionContext(
        event=event,
        correlation_id=event.correlation_id,
        state_store=object(),
        cache=object(),
        logger=object(),
        metadata={"tenant": "acme"},
    )

    assert isinstance(event.payload, Mapping)
    assert isinstance(event.metadata, Mapping)
    assert isinstance(command.payload, Mapping)
    assert isinstance(command.metadata, Mapping)
    assert isinstance(job.metadata, Mapping)
    assert isinstance(result.state_writes[0].value, Mapping)
    assert isinstance(result.cache_writes[0].value, Mapping)
    assert isinstance(result.logs[0].context, Mapping)
    assert isinstance(context.metadata, Mapping)
    assert isinstance(result.commands, tuple)
    assert isinstance(result.state_writes, tuple)
    assert isinstance(result.cache_writes, tuple)
    assert isinstance(result.logs, tuple)

    with pytest.raises(TypeError):
        event.payload["text"] = "bye"

    with pytest.raises(TypeError):
        context.metadata["tenant"] = "other"

    with pytest.raises(AttributeError):
        result.commands.append(command)


def test_handler_result_defaults_to_empty_effects() -> None:
    result = HandlerResult()

    assert result.commands == ()
    assert result.state_writes == ()
    assert result.cache_writes == ()
    assert result.logs == ()


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
