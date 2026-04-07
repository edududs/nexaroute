# Nexaroute MVP Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Nexaroute MVP foundation as a single-process, async, hexagonal event orchestration framework with constructor-based dependency injection, in-memory adapters, and documentation-first delivery.

**Architecture:** Nexaroute will keep `core` pure with Pydantic v2 domain models and strict ABC ports, while `application` owns dispatch, orchestration, and handler resolution. The MVP runtime will dispatch normalized `InboundEvent` instances into `JobEnvelope` items, move them through an in-memory `QueuePort`, and execute them through an in-process `ExecutionStrategyPort` built on `asyncio.TaskGroup`.

**Tech Stack:** Python 3.13, asyncio TaskGroup, Pydantic v2, Rich, pytest, pytest-asyncio

---

## File Structure Map

### Project and packaging
- Modify: `pyproject.toml` — rename the distributable to `nexaroute`, keep runtime dependencies minimal for the MVP, add test tooling, and configure pytest.
- Create: `src/nexaroute/__init__.py` — package root and exported version.
- Modify: `main.py` — bootstrap and run the simple runtime.

### Core domain
- Create: `src/nexaroute/core/__init__.py`
- Create: `src/nexaroute/core/domain/__init__.py`
- Create: `src/nexaroute/core/domain/events.py` — `InboundEvent`
- Create: `src/nexaroute/core/domain/commands.py` — `OutboundCommand`
- Create: `src/nexaroute/core/domain/jobs.py` — `JobEnvelope`
- Create: `src/nexaroute/core/domain/context.py` — `ExecutionContext`
- Create: `src/nexaroute/core/domain/results.py` — `StateWrite`, `CacheWrite`, `LogEntry`, `HandlerResult`

### Core ports
- Create: `src/nexaroute/core/ports/__init__.py`
- Create: `src/nexaroute/core/ports/triggers.py` — `BaseTrigger`, `EventPublisher`
- Create: `src/nexaroute/core/ports/actions.py` — `BaseAction`
- Create: `src/nexaroute/core/ports/queue.py` — `QueuePort`
- Create: `src/nexaroute/core/ports/execution.py` — `ExecutionProcessorPort`, `ExecutionStrategyPort`
- Create: `src/nexaroute/core/ports/cache.py` — `CachePort`
- Create: `src/nexaroute/core/ports/state_store.py` — `StateStorePort`
- Create: `src/nexaroute/core/ports/logger.py` — `LoggerPort`

### Application layer
- Create: `src/nexaroute/application/__init__.py`
- Create: `src/nexaroute/application/handlers.py` — handler type aliases and helper types
- Create: `src/nexaroute/application/registry.py` — `HandlerRegistry`
- Create: `src/nexaroute/application/orchestrator.py` — `Orchestrator`
- Create: `src/nexaroute/application/runtime.py` — `DispatcherRuntime`
- Create: `src/nexaroute/application/bootstrap.py` — `create_simple_runtime`

### In-memory adapters
- Create: `src/nexaroute/adapters/__init__.py`
- Create: `src/nexaroute/adapters/in_memory/__init__.py`
- Create: `src/nexaroute/adapters/in_memory/queue.py` — `InMemoryQueueAdapter`
- Create: `src/nexaroute/adapters/in_memory/execution.py` — `InMemoryExecutionAdapter`
- Create: `src/nexaroute/adapters/in_memory/cache.py` — `InMemoryCacheAdapter`
- Create: `src/nexaroute/adapters/in_memory/state_store.py` — `InMemoryStateStoreAdapter`
- Create: `src/nexaroute/adapters/logging/__init__.py`
- Create: `src/nexaroute/adapters/logging/rich_logger.py` — `RichLoggerAdapter`

### Tests
- Create: `tests/unit/test_package_import.py`
- Create: `tests/unit/core/domain/test_models.py`
- Create: `tests/unit/core/ports/test_port_contracts.py`
- Create: `tests/unit/application/test_registry.py`
- Create: `tests/unit/adapters/in_memory/test_queue_and_storage.py`
- Create: `tests/unit/adapters/in_memory/test_execution.py`
- Create: `tests/unit/application/test_orchestrator.py`
- Create: `tests/integration/test_simple_runtime.py`

### Documentation
- Modify: `README.md` — project overview and quick start
- Create: `docs/architecture/overview.md` — architecture narrative for the MVP
- Create: `docs/guides/bootstrap-simple.md` — simple bootstrap guide
- Create: `docs/reference/inbound-event.md` — event contract reference
- Create: `docs/reference/queue-port.md` — queue contract reference

## Implementation notes before starting

- Keep the MVP dependency list minimal: `pydantic` and `rich` at runtime, `pytest` and `pytest-asyncio` for tests.
- Do **not** add Redis, SQLAlchemy, TaskIQ, RabbitMQ, or Neonize code in this plan; their role is already captured by the approved spec.
- Use Python 3.13 syntax and strong type hints everywhere.
- Prefer timezone-aware datetimes via `datetime.now(UTC)`.
- Add `handler_name: str | None` directly to `InboundEvent` so triggers can route explicitly without stuffing a critical field into untyped metadata.
- Keep delivery semantics in `ExecutionStrategyPort`: it should `ack` on successful `ExecutionProcessorPort.process(job)` and `nack` on raised exceptions. This keeps the core dependency direction clean.

### Task 1: Prepare packaging and test tooling

**Files:**
- Modify: `pyproject.toml`
- Create: `src/nexaroute/__init__.py`
- Test: `tests/unit/test_package_import.py`

- [ ] **Step 1: Update packaging and test configuration**

```toml
[project]
name = "nexaroute"
version = "0.1.0"
description = "Hexagonal event-oriented async orchestration framework"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "pydantic>=2.12.5",
    "rich>=14.3.3",
]

[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Sync the environment**

Run: `uv sync --dev`
Expected: environment updates successfully and installs pytest plus pytest-asyncio.

- [ ] **Step 3: Write the failing import test**

```python
from importlib import import_module


def test_package_imports() -> None:
    module = import_module("nexaroute")
    assert module.__name__ == "nexaroute"
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `uv run pytest tests/unit/test_package_import.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'nexaroute'`.

- [ ] **Step 5: Create the package root**

```python
__all__ = ["__version__"]

__version__ = "0.1.0"
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `uv run pytest tests/unit/test_package_import.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/nexaroute/__init__.py tests/unit/test_package_import.py
git commit -m "chore: initialize nexaroute package and test tooling"
```

### Task 2: Implement the core domain models

**Files:**
- Create: `src/nexaroute/core/__init__.py`
- Create: `src/nexaroute/core/domain/__init__.py`
- Create: `src/nexaroute/core/domain/events.py`
- Create: `src/nexaroute/core/domain/commands.py`
- Create: `src/nexaroute/core/domain/jobs.py`
- Create: `src/nexaroute/core/domain/context.py`
- Create: `src/nexaroute/core/domain/results.py`
- Test: `tests/unit/core/domain/test_models.py`

- [ ] **Step 1: Write the failing domain model tests**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/unit/core/domain/test_models.py -v`
Expected: FAIL with import errors for `nexaroute.core.domain` modules.

- [ ] **Step 3: Implement the domain package markers**

```python
# src/nexaroute/core/__init__.py
__all__ = ["domain", "ports"]

# src/nexaroute/core/domain/__init__.py
from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.domain.results import CacheWrite, HandlerResult, LogEntry, StateWrite

__all__ = [
    "CacheWrite",
    "ExecutionContext",
    "HandlerResult",
    "InboundEvent",
    "JobEnvelope",
    "LogEntry",
    "OutboundCommand",
    "StateWrite",
]
```

- [ ] **Step 4: Implement `InboundEvent` and `OutboundCommand`**

```python
# src/nexaroute/core/domain/events.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class InboundEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    source: str
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    causation_id: str | None = None
    handler_name: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.correlation_id is None:
            object.__setattr__(self, "correlation_id", self.id)

# src/nexaroute/core/domain/commands.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class OutboundCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    target: str
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.correlation_id is None:
            object.__setattr__(self, "correlation_id", self.id)
```

- [ ] **Step 5: Implement `JobEnvelope`, `ExecutionContext`, and `HandlerResult` support types**

```python
# src/nexaroute/core/domain/jobs.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from nexaroute.core.domain.events import InboundEvent


class JobEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    job_id: str = Field(default_factory=lambda: str(uuid4()))
    event: InboundEvent
    handler_name: str | None = None
    routing_key: str | None = None
    correlation_id: str
    causation_id: str | None = None
    attempt: int = 1
    scheduled_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_event(cls, event: InboundEvent) -> "JobEnvelope":
        return cls(
            event=event,
            handler_name=event.handler_name,
            correlation_id=event.correlation_id or event.id,
            causation_id=event.causation_id,
        )

# src/nexaroute/core/domain/context.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from nexaroute.core.domain.events import InboundEvent

if TYPE_CHECKING:
    from nexaroute.core.ports.cache import CachePort
    from nexaroute.core.ports.logger import LoggerPort
    from nexaroute.core.ports.state_store import StateStorePort


@dataclass(slots=True, frozen=True)
class ExecutionContext:
    event: InboundEvent
    correlation_id: str
    state_store: "StateStorePort"
    cache: "CachePort"
    logger: "LoggerPort"
    metadata: dict[str, Any] = field(default_factory=dict)

# src/nexaroute/core/domain/results.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexaroute.core.domain.commands import OutboundCommand

LogLevel = Literal["debug", "info", "warning", "error"]


class StateWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    namespace: str
    key: str
    value: dict[str, Any]


class CacheWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str
    value: dict[str, Any]
    ttl: int | None = None


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level: LogLevel
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: dict[str, Any] = Field(default_factory=dict)


class HandlerResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    commands: list[OutboundCommand] = Field(default_factory=list)
    state_writes: list[StateWrite] = Field(default_factory=list)
    cache_writes: list[CacheWrite] = Field(default_factory=list)
    logs: list[LogEntry] = Field(default_factory=list)
```

- [ ] **Step 6: Run the domain tests to verify they pass**

Run: `uv run pytest tests/unit/core/domain/test_models.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/nexaroute/core/__init__.py src/nexaroute/core/domain tests/unit/core/domain/test_models.py
git commit -m "feat: add typed core domain models"
```

### Task 3: Define the core ports

**Files:**
- Create: `src/nexaroute/core/ports/__init__.py`
- Create: `src/nexaroute/core/ports/triggers.py`
- Create: `src/nexaroute/core/ports/actions.py`
- Create: `src/nexaroute/core/ports/queue.py`
- Create: `src/nexaroute/core/ports/execution.py`
- Create: `src/nexaroute/core/ports/cache.py`
- Create: `src/nexaroute/core/ports/state_store.py`
- Create: `src/nexaroute/core/ports/logger.py`
- Test: `tests/unit/core/ports/test_port_contracts.py`

- [ ] **Step 1: Write the failing port contract tests**

```python
from abc import ABC

from nexaroute.core.ports.actions import BaseAction
from nexaroute.core.ports.cache import CachePort
from nexaroute.core.ports.execution import ExecutionProcessorPort, ExecutionStrategyPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.queue import QueuePort
from nexaroute.core.ports.state_store import StateStorePort
from nexaroute.core.ports.triggers import BaseTrigger


def test_ports_are_abstract_base_classes() -> None:
    for port in (BaseTrigger, BaseAction, QueuePort, ExecutionProcessorPort, ExecutionStrategyPort, CachePort, StateStorePort, LoggerPort):
        assert issubclass(port, ABC)
        assert bool(getattr(port, "__abstractmethods__"))
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/unit/core/ports/test_port_contracts.py -v`
Expected: FAIL with import errors for `nexaroute.core.ports` modules.

- [ ] **Step 3: Implement the ports package marker**

```python
from nexaroute.core.ports.actions import BaseAction
from nexaroute.core.ports.cache import CachePort
from nexaroute.core.ports.execution import ExecutionProcessorPort, ExecutionStrategyPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.queue import QueuePort
from nexaroute.core.ports.state_store import StateStorePort
from nexaroute.core.ports.triggers import BaseTrigger, EventPublisher

__all__ = [
    "BaseAction",
    "BaseTrigger",
    "CachePort",
    "EventPublisher",
    "ExecutionProcessorPort",
    "ExecutionStrategyPort",
    "LoggerPort",
    "QueuePort",
    "StateStorePort",
]
```

- [ ] **Step 4: Implement trigger, action, queue, and execution contracts**

```python
# src/nexaroute/core/ports/triggers.py
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope

EventPublisher = Callable[[InboundEvent], Awaitable[JobEnvelope]]


class BaseTrigger(ABC):
    @abstractmethod
    async def start(self, publisher: EventPublisher) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError

# src/nexaroute/core/ports/actions.py
from __future__ import annotations

from abc import ABC, abstractmethod

from nexaroute.core.domain.commands import OutboundCommand


class BaseAction(ABC):
    @abstractmethod
    def supports(self, command: OutboundCommand) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, command: OutboundCommand) -> None:
        raise NotImplementedError

# src/nexaroute/core/ports/queue.py
from __future__ import annotations

from abc import ABC, abstractmethod

from nexaroute.core.domain.jobs import JobEnvelope


class QueuePort(ABC):
    @abstractmethod
    async def publish(self, job: JobEnvelope) -> None:
        raise NotImplementedError

    @abstractmethod
    async def consume(self) -> JobEnvelope:
        raise NotImplementedError

    @abstractmethod
    async def ack(self, job: JobEnvelope) -> None:
        raise NotImplementedError

    @abstractmethod
    async def nack(self, job: JobEnvelope, reason: str | None = None) -> None:
        raise NotImplementedError

# src/nexaroute/core/ports/execution.py
from __future__ import annotations

from abc import ABC, abstractmethod

from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.queue import QueuePort


class ExecutionProcessorPort(ABC):
    @abstractmethod
    async def process(self, job: JobEnvelope) -> None:
        raise NotImplementedError


class ExecutionStrategyPort(ABC):
    @abstractmethod
    async def start(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError
```

- [ ] **Step 5: Implement cache, state store, and logger contracts**

```python
# src/nexaroute/core/ports/cache.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CachePort(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

# src/nexaroute/core/ports/state_store.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StateStorePort(ABC):
    @abstractmethod
    async def load(self, namespace: str, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, namespace: str, key: str, value: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, namespace: str, key: str) -> None:
        raise NotImplementedError

# src/nexaroute/core/ports/logger.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoggerPort(ABC):
    @abstractmethod
    async def debug(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def info(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def warning(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def error(self, message: str, **context: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exception(self, message: str, **context: Any) -> None:
        raise NotImplementedError
```

- [ ] **Step 6: Run the port contract tests**

Run: `uv run pytest tests/unit/core/ports/test_port_contracts.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/nexaroute/core/ports tests/unit/core/ports/test_port_contracts.py
git commit -m "feat: add core port contracts"
```

### Task 4: Implement handler types and the registry

**Files:**
- Create: `src/nexaroute/application/__init__.py`
- Create: `src/nexaroute/application/handlers.py`
- Create: `src/nexaroute/application/registry.py`
- Test: `tests/unit/application/test_registry.py`

- [ ] **Step 1: Write the failing registry tests**

```python
import pytest

from nexaroute.application.registry import HandlerRegistry
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import HandlerResult


async def sample_handler(_: ExecutionContext) -> HandlerResult:
    return HandlerResult()


def test_registry_resolves_registered_handler() -> None:
    registry = HandlerRegistry()
    registry.register("message.received", sample_handler)

    assert registry.resolve("message.received") is sample_handler


def test_registry_raises_for_missing_handler() -> None:
    registry = HandlerRegistry()

    with pytest.raises(KeyError):
        registry.resolve("missing")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/unit/application/test_registry.py -v`
Expected: FAIL with import errors for `nexaroute.application.registry`.

- [ ] **Step 3: Implement the application package marker and handler typing**

```python
# src/nexaroute/application/__init__.py
from nexaroute.application.registry import HandlerRegistry

__all__ = ["HandlerRegistry"]

# src/nexaroute/application/handlers.py
from __future__ import annotations

from collections.abc import Awaitable, Callable

from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import HandlerResult

type Handler = Callable[[ExecutionContext], Awaitable[HandlerResult]]
```

- [ ] **Step 4: Implement the registry**

```python
from __future__ import annotations

from nexaroute.application.handlers import Handler


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        if name in self._handlers:
            raise ValueError(f"handler '{name}' already registered")
        self._handlers[name] = handler

    def resolve(self, name: str) -> Handler:
        try:
            return self._handlers[name]
        except KeyError as error:
            raise KeyError(f"handler '{name}' is not registered") from error
```

- [ ] **Step 5: Run the registry tests**

Run: `uv run pytest tests/unit/application/test_registry.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/nexaroute/application/__init__.py src/nexaroute/application/handlers.py src/nexaroute/application/registry.py tests/unit/application/test_registry.py
git commit -m "feat: add handler registry"
```

### Task 5: Implement in-memory queue, cache, state store, and rich logger adapters

**Files:**
- Create: `src/nexaroute/adapters/__init__.py`
- Create: `src/nexaroute/adapters/in_memory/__init__.py`
- Create: `src/nexaroute/adapters/in_memory/queue.py`
- Create: `src/nexaroute/adapters/in_memory/cache.py`
- Create: `src/nexaroute/adapters/in_memory/state_store.py`
- Create: `src/nexaroute/adapters/logging/__init__.py`
- Create: `src/nexaroute/adapters/logging/rich_logger.py`
- Test: `tests/unit/adapters/in_memory/test_queue_and_storage.py`

- [ ] **Step 1: Write the failing adapter tests**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/unit/adapters/in_memory/test_queue_and_storage.py -v`
Expected: FAIL with import errors for the adapters.

- [ ] **Step 3: Implement package markers and storage adapters**

```python
# src/nexaroute/adapters/__init__.py
__all__ = ["in_memory", "logging"]

# src/nexaroute/adapters/in_memory/__init__.py
from nexaroute.adapters.in_memory.cache import InMemoryCacheAdapter
from nexaroute.adapters.in_memory.queue import InMemoryQueueAdapter
from nexaroute.adapters.in_memory.state_store import InMemoryStateStoreAdapter

__all__ = [
    "InMemoryCacheAdapter",
    "InMemoryQueueAdapter",
    "InMemoryStateStoreAdapter",
]

# src/nexaroute/adapters/in_memory/queue.py
from __future__ import annotations

import asyncio

from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.queue import QueuePort


class InMemoryQueueAdapter(QueuePort):
    def __init__(self) -> None:
        self._queue: asyncio.Queue[JobEnvelope] = asyncio.Queue()
        self._inflight: dict[str, JobEnvelope] = {}
        self._nacked: dict[str, str | None] = {}

    async def publish(self, job: JobEnvelope) -> None:
        await self._queue.put(job)

    async def consume(self) -> JobEnvelope:
        job = await self._queue.get()
        self._inflight[job.job_id] = job
        return job

    async def ack(self, job: JobEnvelope) -> None:
        self._inflight.pop(job.job_id, None)

    async def nack(self, job: JobEnvelope, reason: str | None = None) -> None:
        self._inflight.pop(job.job_id, None)
        self._nacked[job.job_id] = reason

# src/nexaroute/adapters/in_memory/cache.py
from __future__ import annotations

import asyncio
from typing import Any

from nexaroute.core.ports.cache import CachePort


class InMemoryCacheAdapter(CachePort):
    def __init__(self) -> None:
        self._values: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        value = self._values.get(key)
        if value is None:
            return None
        stored, expires_at = value
        if expires_at is not None and expires_at <= asyncio.get_running_loop().time():
            self._values.pop(key, None)
            return None
        return stored

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = None if ttl is None else asyncio.get_running_loop().time() + ttl
        self._values[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._values.pop(key, None)

# src/nexaroute/adapters/in_memory/state_store.py
from __future__ import annotations

from typing import Any

from nexaroute.core.ports.state_store import StateStorePort


class InMemoryStateStoreAdapter(StateStorePort):
    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = {}

    async def load(self, namespace: str, key: str) -> dict[str, Any] | None:
        return self._data.get(namespace, {}).get(key)

    async def save(self, namespace: str, key: str, value: dict[str, Any]) -> None:
        self._data.setdefault(namespace, {})[key] = value

    async def delete(self, namespace: str, key: str) -> None:
        namespace_data = self._data.get(namespace)
        if namespace_data is None:
            return
        namespace_data.pop(key, None)
```

- [ ] **Step 4: Implement the Rich logger adapter**

```python
# src/nexaroute/adapters/logging/__init__.py
from nexaroute.adapters.logging.rich_logger import RichLoggerAdapter

__all__ = ["RichLoggerAdapter"]

# src/nexaroute/adapters/logging/rich_logger.py
from __future__ import annotations

from typing import Any

from rich.console import Console

from nexaroute.core.ports.logger import LoggerPort


class RichLoggerAdapter(LoggerPort):
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console(stderr=True)

    async def debug(self, message: str, **context: Any) -> None:
        self._console.log(f"[cyan]DEBUG[/cyan] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def info(self, message: str, **context: Any) -> None:
        self._console.log(f"[green]INFO[/green] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def warning(self, message: str, **context: Any) -> None:
        self._console.log(f"[yellow]WARN[/yellow] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def error(self, message: str, **context: Any) -> None:
        self._console.log(f"[red]ERROR[/red] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def exception(self, message: str, **context: Any) -> None:
        self._console.log(f"[bold red]EXCEPTION[/bold red] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)
```

- [ ] **Step 5: Run the adapter tests**

Run: `uv run pytest tests/unit/adapters/in_memory/test_queue_and_storage.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/nexaroute/adapters tests/unit/adapters/in_memory/test_queue_and_storage.py
git commit -m "feat: add in-memory storage and logging adapters"
```

### Task 6: Implement the in-memory execution strategy

**Files:**
- Create: `src/nexaroute/adapters/in_memory/execution.py`
- Test: `tests/unit/adapters/in_memory/test_execution.py`

- [ ] **Step 1: Write the failing execution strategy tests**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/unit/adapters/in_memory/test_execution.py -v`
Expected: FAIL with import errors for `InMemoryExecutionAdapter`.

- [ ] **Step 3: Implement the in-memory execution strategy**

```python
from __future__ import annotations

import asyncio

from nexaroute.core.ports.execution import ExecutionProcessorPort, ExecutionStrategyPort
from nexaroute.core.ports.queue import QueuePort


class InMemoryExecutionAdapter(ExecutionStrategyPort):
    def __init__(self, concurrency: int = 1, poll_interval: float = 0.05) -> None:
        self._concurrency = concurrency
        self._poll_interval = poll_interval
        self._stop_event = asyncio.Event()
        self._supervisor: asyncio.Task[None] | None = None

    async def start(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        if self._supervisor is not None:
            raise RuntimeError("execution strategy already started")
        self._stop_event.clear()
        self._supervisor = asyncio.create_task(self._run(queue, processor))

    async def stop(self) -> None:
        if self._supervisor is None:
            return
        self._stop_event.set()
        await self._supervisor
        self._supervisor = None

    async def _run(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        async with asyncio.TaskGroup() as group:
            for _ in range(self._concurrency):
                group.create_task(self._consume(queue, processor))

    async def _consume(self, queue: QueuePort, processor: ExecutionProcessorPort) -> None:
        while not self._stop_event.is_set():
            try:
                async with asyncio.timeout(self._poll_interval):
                    job = await queue.consume()
            except TimeoutError:
                continue

            try:
                await processor.process(job)
            except Exception as error:
                await queue.nack(job, reason=str(error))
                continue

            await queue.ack(job)
```

- [ ] **Step 4: Run the execution strategy tests**

Run: `uv run pytest tests/unit/adapters/in_memory/test_execution.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/nexaroute/adapters/in_memory/execution.py tests/unit/adapters/in_memory/test_execution.py
git commit -m "feat: add in-memory execution strategy"
```

### Task 7: Implement the orchestrator

**Files:**
- Create: `src/nexaroute/application/orchestrator.py`
- Test: `tests/unit/application/test_orchestrator.py`

- [ ] **Step 1: Write the failing orchestrator tests**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/unit/application/test_orchestrator.py -v`
Expected: FAIL with import errors for `Orchestrator`.

- [ ] **Step 3: Implement the orchestrator**

```python
from __future__ import annotations

from collections.abc import Sequence

from nexaroute.application.registry import HandlerRegistry
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.domain.results import HandlerResult, LogEntry
from nexaroute.core.ports.actions import BaseAction
from nexaroute.core.ports.cache import CachePort
from nexaroute.core.ports.execution import ExecutionProcessorPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.state_store import StateStorePort


class Orchestrator(ExecutionProcessorPort):
    def __init__(
        self,
        *,
        handlers: HandlerRegistry,
        state_store: StateStorePort,
        cache: CachePort,
        logger: LoggerPort,
        actions: Sequence[BaseAction],
    ) -> None:
        self.handlers = handlers
        self.state_store = state_store
        self.cache = cache
        self.logger = logger
        self.actions = list(actions)

    async def process(self, job: JobEnvelope) -> None:
        handler_key = job.handler_name or job.event.name
        handler = self.handlers.resolve(handler_key)
        context = ExecutionContext(
            event=job.event,
            correlation_id=job.correlation_id,
            state_store=self.state_store,
            cache=self.cache,
            logger=self.logger,
            metadata=job.metadata,
        )
        result = await handler(context)
        await self._apply(result)
        await self.logger.info("job processed", job_id=job.job_id, handler=handler_key)

    async def _apply(self, result: HandlerResult) -> None:
        for write in result.state_writes:
            await self.state_store.save(write.namespace, write.key, write.value)

        for write in result.cache_writes:
            await self.cache.set(write.key, write.value, ttl=write.ttl)

        for command in result.commands:
            action = self._resolve_action(command.target)
            await action.execute(command)

        for entry in result.logs:
            await self._log_entry(entry)

    def _resolve_action(self, target: str) -> BaseAction:
        for action in self.actions:
            from nexaroute.core.domain.commands import OutboundCommand
            if action.supports(OutboundCommand(name="probe", target=target)):
                return action
        raise LookupError(f"no action registered for target '{target}'")

    async def _log_entry(self, entry: LogEntry) -> None:
        if entry.level == "debug":
            await self.logger.debug(entry.message, **entry.context)
        elif entry.level == "info":
            await self.logger.info(entry.message, **entry.context)
        elif entry.level == "warning":
            await self.logger.warning(entry.message, **entry.context)
        else:
            await self.logger.error(entry.message, **entry.context)
```

- [ ] **Step 4: Tighten action resolution to avoid probe commands**

```python
# replace the _apply loop and _resolve_action helper in src/nexaroute/application/orchestrator.py
from nexaroute.core.domain.commands import OutboundCommand

    async def _apply(self, result: HandlerResult) -> None:
        for write in result.state_writes:
            await self.state_store.save(write.namespace, write.key, write.value)

        for write in result.cache_writes:
            await self.cache.set(write.key, write.value, ttl=write.ttl)

        for command in result.commands:
            action = self._resolve_action(command)
            await action.execute(command)

        for entry in result.logs:
            await self._log_entry(entry)

    def _resolve_action(self, command: OutboundCommand) -> BaseAction:
        for action in self.actions:
            if action.supports(command):
                return action
        raise LookupError(f"no action registered for target '{command.target}'")
```

- [ ] **Step 5: Run the orchestrator tests**

Run: `uv run pytest tests/unit/application/test_orchestrator.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/nexaroute/application/orchestrator.py tests/unit/application/test_orchestrator.py
git commit -m "feat: add orchestrator effect application"
```

### Task 8: Implement the dispatcher runtime, simple bootstrap, and entry point

**Files:**
- Create: `src/nexaroute/application/runtime.py`
- Create: `src/nexaroute/application/bootstrap.py`
- Modify: `main.py`
- Test: `tests/integration/test_simple_runtime.py`

- [ ] **Step 1: Write the failing runtime integration test**

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/integration/test_simple_runtime.py -v`
Expected: FAIL with import errors for `create_simple_runtime` and `DispatcherRuntime`.

- [ ] **Step 3: Implement the dispatcher runtime**

```python
from __future__ import annotations

from collections.abc import Sequence

from nexaroute.core.domain.events import InboundEvent
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.ports.execution import ExecutionStrategyPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.queue import QueuePort
from nexaroute.core.ports.triggers import BaseTrigger


class DispatcherRuntime:
    def __init__(
        self,
        *,
        queue: QueuePort,
        execution: ExecutionStrategyPort,
        orchestrator,
        triggers: Sequence[BaseTrigger],
        logger: LoggerPort,
    ) -> None:
        self.queue = queue
        self.execution = execution
        self.orchestrator = orchestrator
        self.triggers = list(triggers)
        self.logger = logger
        self._started = False

    async def publish_event(self, event: InboundEvent) -> JobEnvelope:
        job = JobEnvelope.from_event(event)
        await self.queue.publish(job)
        await self.logger.debug("event dispatched", event_name=event.name, job_id=job.job_id)
        return job

    async def start(self) -> None:
        if self._started:
            return
        await self.execution.start(self.queue, self.orchestrator)
        for trigger in self.triggers:
            await trigger.start(self.publish_event)
        self._started = True
        await self.logger.info("runtime started", trigger_count=len(self.triggers))

    async def stop(self) -> None:
        if not self._started:
            return
        for trigger in self.triggers:
            await trigger.stop()
        await self.execution.stop()
        self._started = False
        await self.logger.info("runtime stopped")
```

- [ ] **Step 4: Implement the simple bootstrap and main entry point**

```python
# src/nexaroute/application/bootstrap.py
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

# main.py
import asyncio

from nexaroute.application.bootstrap import create_simple_runtime


async def main() -> None:
    runtime = create_simple_runtime(triggers=[], handlers={})
    await runtime.start()
    await runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 5: Run the integration test**

Run: `uv run pytest tests/integration/test_simple_runtime.py -v`
Expected: PASS.

- [ ] **Step 6: Run the full test suite**

Run: `uv run pytest -v`
Expected: all current tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/nexaroute/application/runtime.py src/nexaroute/application/bootstrap.py main.py tests/integration/test_simple_runtime.py
git commit -m "feat: add simple dispatcher runtime bootstrap"
```

### Task 9: Write the MVP documentation

**Files:**
- Modify: `README.md`
- Create: `docs/architecture/overview.md`
- Create: `docs/guides/bootstrap-simple.md`
- Create: `docs/reference/inbound-event.md`
- Create: `docs/reference/queue-port.md`

- [ ] **Step 1: Write the README**

```markdown
# Nexaroute

Nexaroute is an async, event-oriented automation and orchestration framework built on Hexagonal Architecture.

## MVP scope

- autonomous runtime
- typed domain models
- strict ports
- in-memory queue and execution strategy
- constructor-based dependency injection

## Quick start

```python
from nexaroute.application.bootstrap import create_simple_runtime

runtime = create_simple_runtime(
    triggers=[],
    handlers={},
)
```

See `docs/architecture/overview.md` and `docs/guides/bootstrap-simple.md` for details.
```

- [ ] **Step 2: Write the architecture overview**

```markdown
# Nexaroute Architecture Overview

## Layers

- `core` holds typed domain models and strict ports.
- `application` owns handler resolution, orchestration, and runtime dispatch.
- `adapters` implement replaceable infrastructure.

## MVP flow

`Trigger -> DispatcherRuntime -> JobEnvelope -> QueuePort -> ExecutionStrategyPort -> Orchestrator -> HandlerResult -> Actions/State/Cache/Logger`

## Why this shape

The runtime keeps ingress responsive while the execution strategy controls concurrency. The core remains infrastructure-agnostic.
```

- [ ] **Step 3: Write the bootstrap and contract reference docs**

```markdown
# docs/guides/bootstrap-simple.md

## Simple bootstrap

Use `create_simple_runtime()` to compose the MVP runtime with in-memory adapters.

```python
runtime = create_simple_runtime(
    triggers=[],
    handlers={"message.received": handler},
    concurrency=4,
)
```

The runtime starts triggers, dispatches `InboundEvent` instances into `JobEnvelope` items, and processes them in-process with `asyncio.TaskGroup`.
```

```markdown
# docs/reference/inbound-event.md

## InboundEvent

`InboundEvent` is the normalized ingress model.

### Fields
- `id`
- `name`
- `source`
- `payload`
- `metadata`
- `occurred_at`
- `correlation_id`
- `causation_id`
- `handler_name`

`handler_name` exists so a trigger may route directly to a registered handler when needed.
```

```markdown
# docs/reference/queue-port.md

## QueuePort

`QueuePort` transports `JobEnvelope` items.

### Methods
- `publish(job)`
- `consume()`
- `ack(job)`
- `nack(job, reason=None)`

In the MVP, `InMemoryQueueAdapter` implements this contract using `asyncio.Queue` plus explicit in-flight tracking.
```

- [ ] **Step 4: Verify docs and test suite**

Run: `uv run pytest -v`
Expected: all tests still PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/architecture/overview.md docs/guides/bootstrap-simple.md docs/reference/inbound-event.md docs/reference/queue-port.md
git commit -m "docs: add nexaroute mvp architecture guides"
```

## Plan self-review

- **Spec coverage:** Tasks 2 and 3 implement the typed domain and strict ports; Tasks 5 through 8 implement the simple bootstrap, dispatch model, queue, execution strategy, and orchestrator; Task 9 turns the approved design into permanent docs.
- **Placeholder scan:** No `TODO`, `TBD`, or deferred code markers remain in task steps.
- **Type consistency:** `InboundEvent`, `JobEnvelope`, `HandlerResult`, `QueuePort`, `ExecutionProcessorPort`, `ExecutionStrategyPort`, `Handler`, `HandlerRegistry`, `Orchestrator`, and `DispatcherRuntime` use the same names and signatures across tasks.
