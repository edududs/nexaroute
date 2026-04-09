from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

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


@pytest.mark.parametrize(
    ("factory", "field_name"),
    [
        (lambda dt: InboundEvent(name="message.received", source="test", payload={}, occurred_at=dt), "occurred_at"),
        (
            lambda dt: OutboundCommand(name="notify", target="discord", payload={}, created_at=dt),
            "created_at",
        ),
        (
            lambda dt: JobEnvelope(
                event=InboundEvent(name="message.received", source="test", payload={}),
                correlation_id="corr-1",
                scheduled_at=dt,
            ),
            "scheduled_at",
        ),
        (lambda dt: LogEntry(level="info", message="processed", timestamp=dt), "timestamp"),
    ],
)
def test_models_reject_naive_datetimes(factory: Callable[[datetime], object], field_name: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        factory(datetime(2026, 1, 2, 3, 4, 5))

    errors = exc_info.value.errors()

    assert errors[0]["loc"] == (field_name,)
    assert errors[0]["type"] == "timezone_aware"


@pytest.mark.parametrize(
    ("factory", "field_name"),
    [
        (lambda dt: InboundEvent(name="message.received", source="test", payload={}, occurred_at=dt), "occurred_at"),
        (
            lambda dt: OutboundCommand(name="notify", target="discord", payload={}, created_at=dt),
            "created_at",
        ),
        (
            lambda dt: JobEnvelope(
                event=InboundEvent(name="message.received", source="test", payload={}),
                correlation_id="corr-1",
                scheduled_at=dt,
            ),
            "scheduled_at",
        ),
        (lambda dt: LogEntry(level="info", message="processed", timestamp=dt), "timestamp"),
    ],
)
def test_models_normalize_aware_datetimes_to_utc(factory: Callable[[datetime], object], field_name: str) -> None:
    source_dt = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=5, minutes=30)))

    model = factory(source_dt)
    normalized = getattr(model, field_name)

    assert normalized.tzinfo is UTC
    assert normalized == datetime(2026, 1, 1, 21, 34, 5, tzinfo=UTC)


@pytest.mark.parametrize("attempt", [0, -1])
def test_job_envelope_rejects_non_positive_attempts(attempt: int) -> None:
    event = InboundEvent(name="message.received", source="test", payload={})

    with pytest.raises(ValidationError) as exc_info:
        JobEnvelope(event=event, correlation_id=event.correlation_id, attempt=attempt)

    errors = exc_info.value.errors()

    assert errors[0]["loc"] == ("attempt",)
    assert errors[0]["type"] == "greater_than_equal"


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


def test_value_objects_deep_freeze_nested_mappings_and_sequences() -> None:
    event = InboundEvent(
        name="message.received",
        source="test",
        payload={"nested": {"items": ["first", {"key": "value"}]}},
        metadata={"flags": ["a", "b"]},
    )
    command = OutboundCommand(
        name="notify",
        target="discord",
        payload={"nested": {"items": ["first", {"key": "value"}]}},
        metadata={"channels": ["ops"]},
    )
    job = JobEnvelope(
        event=event,
        correlation_id=event.correlation_id,
        metadata={"routes": [{"name": "default"}]},
    )
    state_write = StateWrite(namespace="messages", key="1", value={"nested": {"saved": [True]}})
    cache_write = CacheWrite(key="latest", value={"nested": [{"id": "1"}]}, ttl=60)
    log = LogEntry(level="info", message="processed", context={"nested": {"events": ["message.received"]}})
    context = ExecutionContext(
        event=event,
        correlation_id=event.correlation_id,
        state_store=object(),
        cache=object(),
        logger=object(),
        metadata={"nested": {"tenants": ["acme"]}},
    )

    assert isinstance(event.payload["nested"], Mapping)
    assert isinstance(event.payload["nested"]["items"], tuple)
    assert isinstance(event.payload["nested"]["items"][1], Mapping)
    assert isinstance(command.payload["nested"]["items"], tuple)
    assert isinstance(command.metadata["channels"], tuple)
    assert isinstance(job.metadata["routes"], tuple)
    assert isinstance(job.metadata["routes"][0], Mapping)
    assert isinstance(state_write.value["nested"]["saved"], tuple)
    assert isinstance(cache_write.value["nested"], tuple)
    assert isinstance(cache_write.value["nested"][0], Mapping)
    assert isinstance(log.context["nested"]["events"], tuple)
    assert isinstance(context.metadata["nested"]["tenants"], tuple)

    with pytest.raises(TypeError):
        event.payload["nested"]["items"][1]["key"] = "changed"

    with pytest.raises(TypeError):
        command.payload["nested"]["items"][1]["key"] = "changed"

    with pytest.raises(TypeError):
        job.metadata["routes"][0]["name"] = "priority"

    with pytest.raises(TypeError):
        state_write.value["nested"]["saved"][0] = False

    with pytest.raises(TypeError):
        cache_write.value["nested"][0]["id"] = "2"

    with pytest.raises(TypeError):
        log.context["nested"]["events"][0] = "other"

    with pytest.raises(TypeError):
        context.metadata["nested"]["tenants"][0] = "other"


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
