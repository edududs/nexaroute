import asyncio

import pytest

from nexaroute.adapters.in_memory.execution import InMemoryExecutionAdapter
from nexaroute.adapters.in_memory.queue import InMemoryQueueAdapter
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.execution import ExecutionProcessorPort


class RecordingProcessor(ExecutionProcessorPort):
    def __init__(self) -> None:
        self.processed: list[str] = []
        self.seen = asyncio.Event()

    async def process(self, job: JobEnvelope) -> None:
        self.processed.append(job.job_id)
        self.seen.set()


@pytest.mark.parametrize("concurrency", [0, -1])
def test_execution_strategy_rejects_non_positive_concurrency(concurrency: int) -> None:
    with pytest.raises(ValueError, match="concurrency must be at least 1"):
        InMemoryExecutionAdapter(concurrency=concurrency)


@pytest.mark.asyncio
async def test_execution_strategy_processes_queued_jobs() -> None:
    queue = InMemoryQueueAdapter()
    processor = RecordingProcessor()
    strategy = InMemoryExecutionAdapter(concurrency=1)
    job = JobEnvelope.from_event(InboundEvent(name="message.received", source="test", payload={}))

    await strategy.start(queue, processor)
    await queue.publish(job)
    await asyncio.wait_for(processor.seen.wait(), timeout=1)
    await strategy.stop()

    assert processor.processed == [job.job_id]
