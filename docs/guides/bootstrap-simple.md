## Simple bootstrap

Use `create_simple_runtime()` to compose the MVP runtime with in-memory adapters.

```python
import asyncio

from nexaroute.application.bootstrap import create_simple_runtime
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import HandlerResult


async def handle_message(_: ExecutionContext) -> HandlerResult:
    return HandlerResult()


async def main() -> None:
    runtime = create_simple_runtime(
        triggers=[],
        handlers={"message.received": handle_message},
        concurrency=4,
    )

    await runtime.start()
    try:
        # Runtime triggers and in-process execution stay active until stopped.
        await asyncio.sleep(1)
    finally:
        await runtime.stop()


asyncio.run(main())
```

After startup, the runtime starts triggers, dispatches `InboundEvent` instances into `JobEnvelope` items, and processes them in-process with `asyncio.TaskGroup` until `stop()` is awaited.
