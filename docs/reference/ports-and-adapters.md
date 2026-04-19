# Ports And Adapters Reference

## Ingress And Dispatch

### `BaseTrigger`

- `start(publisher)`
- `stop()`

Purpose: turn external signals into `InboundEvent` publications.

### `QueuePort`

- `publish(job)`
- `consume()`
- `ack(job)`
- `nack(job, reason=None)`

Purpose: durable or ephemeral transport for `JobEnvelope`.

### `ExecutionStrategyPort`

- `start(queue, processor)`
- `stop()`

Purpose: concurrency model and worker lifecycle.

## Processing

### `ExecutionProcessorPort`

- `process(job)`

`Orchestrator` is the default implementation.

## Side-Effect Ports

### `StateStorePort`

- `load(namespace, key)`
- `save(namespace, key, value)`
- `delete(namespace, key)`

### `CachePort`

- `get(key)`
- `set(key, value, ttl=None)`
- `delete(key)`

### `LoggerPort`

- `debug/info/warning/error/exception`

### `BaseAction`

- `supports(command)`
- `execute(command)`

Purpose: command target routing for infrastructure actions.

## Adapter Guidance

- Keep adapters thin and deterministic.
- Validate payloads at adapter boundaries.
- Keep retry/idempotency semantics explicit.
- Never bury business rules in adapters.
