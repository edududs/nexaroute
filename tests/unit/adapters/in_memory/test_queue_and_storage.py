from io import StringIO

import pytest
from rich.console import Console

from nexaroute.adapters.in_memory.cache import InMemoryCacheAdapter
from nexaroute.adapters.in_memory.queue import InMemoryQueueAdapter
from nexaroute.adapters.in_memory.state_store import InMemoryStateStoreAdapter
from nexaroute.adapters.logging.rich_logger import RichLoggerAdapter
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope


@pytest.mark.asyncio
async def test_in_memory_queue_round_trip() -> None:
    queue = InMemoryQueueAdapter()
    job = JobEnvelope.from_event(InboundEvent(name="message.received", source="test", payload={}))

    await queue.publish(job)
    consumed = await queue.consume()
    await queue.ack(consumed)

    assert consumed == job


@pytest.mark.asyncio
async def test_in_memory_cache_respects_set_get_delete() -> None:
    cache = InMemoryCacheAdapter()

    await cache.set("latest", {"id": "1"}, ttl=60)
    assert await cache.get("latest") == {"id": "1"}

    await cache.delete("latest")
    assert await cache.get("latest") is None


@pytest.mark.asyncio
async def test_in_memory_state_store_round_trip() -> None:
    store = InMemoryStateStoreAdapter()

    await store.save("messages", "1", {"text": "hello"})
    assert await store.load("messages", "1") == {"text": "hello"}

    await store.delete("messages", "1")
    assert await store.load("messages", "1") is None


@pytest.mark.asyncio
async def test_in_memory_state_store_save_isolates_nested_mutation() -> None:
    store = InMemoryStateStoreAdapter()
    payload = {"text": "hello", "meta": {"tags": ["initial"]}}

    await store.save("messages", "1", payload)
    payload["meta"]["tags"].append("mutated")

    assert await store.load("messages", "1") == {
        "text": "hello",
        "meta": {"tags": ["initial"]},
    }


@pytest.mark.asyncio
async def test_in_memory_state_store_load_returns_deep_copy() -> None:
    store = InMemoryStateStoreAdapter()

    await store.save("messages", "1", {"text": "hello", "meta": {"tags": ["initial"]}})
    loaded = await store.load("messages", "1")
    assert loaded is not None

    loaded["meta"]["tags"].append("mutated")

    assert await store.load("messages", "1") == {
        "text": "hello",
        "meta": {"tags": ["initial"]},
    }


@pytest.mark.asyncio
async def test_rich_logger_methods_do_not_raise() -> None:
    logger = RichLoggerAdapter()

    await logger.info("runtime started", component="test")
    await logger.error("runtime failed", component="test")


@pytest.mark.asyncio
async def test_rich_logger_exception_includes_active_traceback() -> None:
    output = StringIO()
    logger = RichLoggerAdapter(console=Console(file=output, stderr=True, force_terminal=False))

    try:
        raise ValueError("boom")
    except ValueError:
        await logger.exception("runtime failed", component="test")

    rendered = output.getvalue()

    assert "EXCEPTION" in rendered
    assert "runtime failed" in rendered
    assert "ValueError: boom" in rendered
    assert "Traceback" in rendered
    assert "component" in rendered
    assert "test" in rendered
    assert "test_rich_logger_exception_includes_active_traceback" in rendered


@pytest.mark.asyncio
async def test_rich_logger_exception_outside_exception_context_does_not_raise() -> None:
    output = StringIO()
    logger = RichLoggerAdapter(console=Console(file=output, stderr=True, force_terminal=False))

    await logger.exception("runtime failed", component="test")

    rendered = output.getvalue()

    assert "EXCEPTION" in rendered
    assert "runtime failed" in rendered
    assert "component" in rendered
    assert "test" in rendered
    assert "Traceback" not in rendered
    assert "NoneType: None" not in rendered
    assert "ValueError: boom" not in rendered
    assert "test_rich_logger_exception_includes_active_traceback" not in rendered
