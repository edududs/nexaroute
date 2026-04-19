# Nexaroute Architecture Overview

## Layers

- `core` holds typed domain models and strict ports.
- `application` owns handler resolution, orchestration, and runtime dispatch.
- `adapters` implement replaceable infrastructure.

## MVP flow

`Trigger -> DispatcherRuntime -> JobEnvelope -> QueuePort -> ExecutionStrategyPort -> Orchestrator -> HandlerResult -> Actions/State/Cache/Logger`

## Why this shape

The runtime keeps ingress responsive while the execution strategy controls concurrency. The core remains infrastructure-agnostic.

## Continue Reading

- `system-design.md` for deeper runtime responsibilities and guarantees
- `../reference/domain-models.md` for model-level contracts
- `../reference/ports-and-adapters.md` for integration boundaries
