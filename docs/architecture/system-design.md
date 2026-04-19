# System Design

## Layering

- `core/`: domain models and abstract ports.
- `application/`: orchestration and runtime coordination.
- `adapters/`: concrete implementations for ports.

## Execution Path

`Trigger -> publish_event() -> QueuePort.publish() -> ExecutionStrategyPort.consume/process -> Orchestrator.process() -> HandlerResult application`

## Orchestrator Responsibilities

The orchestrator:

- resolves handlers by event name or explicit `handler_name`
- creates `ExecutionContext`
- invokes handler
- applies result in strict order:
  1. state writes
  2. cache writes
  3. commands via actions
  4. logs

## Runtime Guarantees (MVP)

- startup is idempotent (`start()` can be called safely multiple times)
- shutdown attempts best-effort cleanup
- partial failures during shutdown are surfaced, not silently ignored
- trigger startup failures attempt execution cleanup

## Current MVP Scope

- in-memory queue and execution strategy
- in-memory state/cache adapters
- constructor-based dependency injection

For production scenarios, replace adapters while keeping handler logic unchanged.
