import pytest

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
async def test_rich_logger_methods_do_not_raise() -> None:
    logger = RichLoggerAdapter()

    await logger.info("runtime started", component="test")
    await logger.error("runtime failed", component="test")
