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
import asyncio

from nexaroute.application.bootstrap import create_simple_runtime


async def main() -> None:
    runtime = create_simple_runtime(
        triggers=[],
        handlers={},
    )

    await runtime.start()
    try:
        # Runtime triggers and in-process execution stay active until stopped.
        await asyncio.sleep(1)
    finally:
        await runtime.stop()


asyncio.run(main())
```

See `docs/architecture/overview.md` and `docs/guides/bootstrap-simple.md` for details.
