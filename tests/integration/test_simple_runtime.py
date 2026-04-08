import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from nexaroute.application.runtime import DispatcherRuntime
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.domain.results import HandlerResult, StateWrite
from nexaroute.core.ports.execution import ExecutionProcessorPort, ExecutionStrategyPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.queue import QueuePort
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


class StubQueue(QueuePort):
    async def publish(self, job: JobEnvelope) -> None:
        _ = job
        return None

    async def consume(self) -> JobEnvelope:
        raise AssertionError("consume should not be called")

    async def ack(self, job: JobEnvelope) -> None:
        _ = job
        return None

    async def nack(self, job: JobEnvelope, reason: str | None = None) -> None:
        _ = (job, reason)
        return None


class StubLogger(LoggerPort):
    async def debug(self, message: str, **context: Any) -> None:
        _ = (message, context)
        return None

    async def info(self, message: str, **context: Any) -> None:
        _ = (message, context)
        return None

    async def warning(self, message: str, **context: Any) -> None:
        _ = (message, context)
        return None

    async def error(self, message: str, **context: Any) -> None:
        _ = (message, context)
        return None

    async def exception(self, message: str, **context: Any) -> None:
        _ = (message, context)
        return None


class StubProcessor(ExecutionProcessorPort):
    async def process(self, job: JobEnvelope) -> None:
        _ = job
        return None


class RecordingExecution(ExecutionStrategyPort):
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0

    async def start(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        _ = (queue, processor)
        self.start_calls += 1

    async def stop(self) -> None:
        self.stop_calls += 1


class FailingStartTrigger(BaseTrigger):
    async def start(self, publisher: EventPublisher) -> None:
        _ = publisher
        raise RuntimeError("trigger start failed")

    async def stop(self) -> None:
        return None


class FailingStopTrigger(BaseTrigger):
    def __init__(self) -> None:
        self.started = False
        self.stop_calls = 0

    async def start(self, publisher: EventPublisher) -> None:
        _ = publisher
        self.started = True

    async def stop(self) -> None:
        self.stop_calls += 1
        raise RuntimeError("trigger stop failed")


@pytest.mark.asyncio
async def test_runtime_cleans_up_execution_when_trigger_start_fails() -> None:
    execution = RecordingExecution()
    runtime = DispatcherRuntime(
        queue=StubQueue(),
        execution=execution,
        orchestrator=StubProcessor(),
        triggers=[FailingStartTrigger()],
        logger=StubLogger(),
    )

    with pytest.raises(RuntimeError, match="trigger start failed"):
        await runtime.start()

    assert execution.start_calls == 1
    assert execution.stop_calls == 1


@pytest.mark.asyncio
async def test_runtime_stops_execution_even_when_trigger_stop_fails() -> None:
    execution = RecordingExecution()
    trigger = FailingStopTrigger()
    runtime = DispatcherRuntime(
        queue=StubQueue(),
        execution=execution,
        orchestrator=StubProcessor(),
        triggers=[trigger],
        logger=StubLogger(),
    )

    await runtime.start()

    with pytest.raises(RuntimeError, match="trigger stop failed"):
        await runtime.stop()

    assert trigger.started is True
    assert trigger.stop_calls == 1
    assert execution.start_calls == 1
    assert execution.stop_calls == 1


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


def test_root_main_runs_from_source_checkout_without_pytest_pythonpath() -> None:
    project_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
