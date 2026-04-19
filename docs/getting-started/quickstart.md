# Quickstart

This is the smallest runnable Nexaroute setup.

```python
import asyncio

from nexaroute.application.bootstrap import create_simple_runtime
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import HandlerResult


async def on_message(_: ExecutionContext) -> HandlerResult:
    return HandlerResult()


async def main() -> None:
    runtime = create_simple_runtime(
        triggers=[],
        handlers={"message.received": on_message},
        concurrency=2,
    )
    await runtime.start()
    try:
        await asyncio.sleep(1)
    finally:
        await runtime.stop()


asyncio.run(main())
```

## What Happens

1. `create_simple_runtime()` wires in-memory adapters.
2. `start()` starts execution strategy and triggers.
3. Events become `JobEnvelope` instances and are consumed by workers.
4. `stop()` performs graceful component shutdown.
