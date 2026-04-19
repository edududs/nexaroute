# Domain Models Reference

## `InboundEvent`

Normalized incoming event model.

Key fields:

- `id`, `name`, `source`
- `payload`, `metadata`
- `occurred_at` (UTC-normalized)
- `correlation_id`, `causation_id`
- `handler_name`

Notes:

- immutable/frozen model
- nested payload structures are frozen to avoid accidental mutation

## `JobEnvelope`

Queue and scheduling metadata around an event.

Key fields:

- `job_id`
- `event`
- `handler_name`, `routing_key`
- `correlation_id`, `causation_id`
- `attempt`, `scheduled_at`
- `metadata`

## `ExecutionContext`

Handler execution input:

- `event`
- `correlation_id`
- `state_store`, `cache`, `logger`
- `metadata`

## `OutboundCommand`

Represents a requested outbound action.

Key fields:

- `id`, `name`, `target`
- `payload`, `metadata`
- `created_at`
- `correlation_id`

## `HandlerResult`

Declares all side effects from a handler:

- `commands`
- `state_writes`
- `cache_writes`
- `logs`

Helper models:

- `StateWrite`
- `CacheWrite`
- `LogEntry`
