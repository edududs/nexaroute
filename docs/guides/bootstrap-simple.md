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
