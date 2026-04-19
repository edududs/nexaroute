# Core Concepts

## 1. Event

`InboundEvent` is the canonical ingress payload. It carries:

- identity (`id`)
- semantic name (`name`)
- origin (`source`)
- data (`payload`, `metadata`)
- tracing fields (`correlation_id`, `causation_id`)

## 2. Job

`JobEnvelope` is runtime-level work metadata around an event:

- queue identity (`job_id`)
- routing (`handler_name`, `routing_key`)
- retry metadata (`attempt`, `scheduled_at`)

## 3. Handler

A handler is an async function:

- input: `ExecutionContext`
- output: `HandlerResult`

The handler should decide *what* should happen, not *how* infrastructure executes it.

## 4. Result

`HandlerResult` declares side effects:

- `state_writes`
- `cache_writes`
- `commands`
- `logs`

The orchestrator applies these effects via ports/actions.

## 5. Ports

Ports define infrastructure contracts:

- `QueuePort`
- `ExecutionStrategyPort`
- `StateStorePort`
- `CachePort`
- `LoggerPort`
- `BaseAction`
- `BaseTrigger`

## 6. Runtime Lifecycle

`DispatcherRuntime` owns startup/shutdown sequencing:

1. start execution strategy
2. start triggers
3. dispatch events to queue
4. stop triggers and execution gracefully
