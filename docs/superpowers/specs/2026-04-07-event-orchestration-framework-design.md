# Nexaroute — Event-Oriented Automation and Orchestration Framework Design

Date: 2026-04-07
Status: Approved for planning
Project: Nexaroute

## 1. Overview

Nexaroute is a Python asynchronous framework for autonomous, event-oriented automation and orchestration. Its foundation must be intentionally simple, runnable in a single process with native Python primitives, and strictly designed around Hexagonal Architecture (Ports and Adapters).

The core of Nexaroute must remain infrastructure-agnostic. Technologies such as TaskIQ, RabbitMQ, Redis, SQLAlchemy, Rich, Neonize, Discord, Slack, or any future tool are implementation details that live exclusively in adapters. The framework must be able to start with in-memory execution and evolve toward broker-backed, distributed, or multi-runtime topologies without changing the core model.

This design also adopts spec-driven development as a project rule. Architecture, contracts, and runtime behavior are specified before implementation. Documentation is treated as part of the product.

## 2. Goals

### 2.1 Primary goals

- Provide an autonomous runtime that stays active and keeps listening for triggers.
- Accept external triggers from multiple sources such as messaging platforms, bots, webhooks, scheduled jobs, or other systems.
- Normalize incoming inputs into a stable internal model.
- Dispatch work without blocking the ingress loop.
- Execute handlers with asynchronous concurrency in the MVP.
- Keep execution topology replaceable.
- Encapsulate infrastructure integrations behind strict ports.
- Make the framework easy to bootstrap in a simple in-memory mode.
- Preserve a natural path toward robust adapters such as TaskIQ, Redis, SQLAlchemy, and Rich.

### 2.2 Non-goals for the MVP

The MVP explicitly does not include:

- workflow DSLs
- saga coordinators
- rule engines
- plugin marketplaces
- visual flow editors
- distributed consensus
- mandatory external workers
- mandatory broker infrastructure
- mandatory retries, dead-letter queues, or idempotency layers

Those features may be added later through the same architectural boundaries.

## 3. Architectural principles

1. **Core first, adapters second**
   The core defines stable contracts and semantic models. Infrastructure is replaceable.

2. **Execution topology is replaceable**
   The framework must support in-process asynchronous execution first and external worker execution later.

3. **Triggers dispatch, handlers decide**
   Trigger adapters listen and normalize. Business logic lives in handlers.

4. **Orchestrator applies effects**
   Handlers return structured results; the orchestrator applies state, cache, logging, and action side effects.

5. **Constructor-based dependency injection**
   Framework composition uses explicit constructor parameters rather than fluent builder chaining.

6. **Strong typing everywhere**
   The framework follows state-of-the-art Python typing practices as of April 2026, with explicit type hints, clear model boundaries, and modern async lifecycle design.

7. **Specification precedes implementation**
   Specs, plans, and architecture docs are required artifacts, not optional extras.

## 4. High-level runtime model

Nexaroute runs as an autonomous application that keeps listening for external input while delegating processing work through an internal dispatch model.

### 4.1 Flow

```text
External Source
  -> Trigger Adapter
  -> DispatcherRuntime
  -> JobEnvelope
  -> QueuePort
  -> ExecutionStrategyPort
  -> Orchestrator
  -> HandlerRegistry
  -> HandlerResult
  -> StateStore / Cache / Logger / Actions
```

### 4.2 Runtime responsibilities

#### DispatcherRuntime

The dispatcher runtime is the ingress-facing runtime layer.

Responsibilities:
- start and stop trigger adapters
- receive normalized `InboundEvent` objects
- resolve a logical target when needed
- wrap work in a `JobEnvelope`
- publish jobs to the configured queue
- keep ingress responsive and non-blocking

#### ExecutionStrategyPort

The execution strategy defines how queued jobs are consumed and processed.

MVP default:
- in-memory queue
- same process
- asynchronous concurrency via `asyncio.TaskGroup`

Future options:
- inline scheduling
- broker-backed workers
- external execution adapters

#### Orchestrator

The orchestrator is the semantic execution layer.

Responsibilities:
- consume a `JobEnvelope`
- build an `ExecutionContext`
- resolve the target handler through the registry
- execute the handler
- apply returned effects in a controlled order
- log success and failure
- acknowledge or reject execution through queue semantics

#### HandlerRegistry

The registry maps work to handlers.

Supported resolution in the MVP:
- explicit `handler_name`
- fallback by `event.name`

This keeps the runtime simple while preserving a path toward richer routing later.

## 5. Core boundaries

The core must be pure and free of infrastructure dependencies except for Pydantic v2 for model validation and typing-friendly data modeling.

### 5.1 Core layers

```text
core/
├── domain/
└── ports/
```

### 5.2 Domain responsibilities

The domain contains stable, infrastructure-agnostic data shapes used by the application and adapters.

### 5.3 Ports responsibilities

The ports define contracts for all external interaction and runtime topology seams.

## 6. Proposed directory layout

```text
my_app3/
├── pyproject.toml
├── README.md
├── main.py
├── docs/
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── runtime-model.md
│   │   ├── ports-and-adapters.md
│   │   └── adr/
│   │       ├── 001-job-envelope.md
│   │       ├── 002-execution-strategy.md
│   │       └── 003-handler-registry.md
│   ├── guides/
│   │   ├── bootstrap-simple.md
│   │   ├── bootstrap-robust.md
│   │   ├── writing-triggers.md
│   │   ├── writing-actions.md
│   │   └── writing-handlers.md
│   ├── reference/
│   │   ├── inbound-event.md
│   │   ├── outbound-command.md
│   │   ├── job-envelope.md
│   │   ├── queue-port.md
│   │   ├── execution-port.md
│   │   ├── state-store-port.md
│   │   └── cache-port.md
│   └── superpowers/
│       └── specs/
│           └── 2026-04-07-event-orchestration-framework-design.md
├── src/
│   └── nexaroute/
│       ├── core/
│       │   ├── domain/
│       │   │   ├── events.py
│       │   │   ├── commands.py
│       │   │   ├── jobs.py
│       │   │   ├── context.py
│       │   │   └── results.py
│       │   └── ports/
│       │       ├── triggers.py
│       │       ├── actions.py
│       │       ├── queue.py
│       │       ├── execution.py
│       │       ├── cache.py
│       │       ├── state_store.py
│       │       └── logger.py
│       ├── application/
│       │   ├── dispatcher.py
│       │   ├── orchestrator.py
│       │   ├── runtime.py
│       │   ├── registry.py
│       │   ├── handlers.py
│       │   └── bootstrap.py
│       ├── adapters/
│       │   ├── in_memory/
│       │   │   ├── queue.py
│       │   │   ├── execution.py
│       │   │   ├── cache.py
│       │   │   ├── state_store.py
│       │   │   └── logger.py
│       │   ├── queue/
│       │   │   └── taskiq_rabbitmq.py
│       │   ├── execution/
│       │   │   └── taskiq_execution.py
│       │   ├── cache/
│       │   │   └── redis_cache.py
│       │   ├── state/
│       │   │   └── sqlalchemy_postgres.py
│       │   ├── logging/
│       │   │   └── rich_logger.py
│       │   ├── triggers/
│       │   │   └── neonize_trigger.py
│       │   └── actions/
│       │       └── discord_action.py
│       └── bootstrap/
│           ├── simple.py
│           └── robust.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

## 7. Domain model

The domain model is intentionally small.

### 7.1 InboundEvent

Represents normalized input from any external source.

Suggested fields:
- `id`
- `name`
- `source`
- `payload`
- `metadata`
- `occurred_at`
- `correlation_id`
- `causation_id | None`

### 7.2 OutboundCommand

Represents an intention to execute a side effect through an action adapter.

Suggested fields:
- `id`
- `name`
- `target`
- `payload`
- `metadata`
- `created_at`
- `correlation_id`

### 7.3 JobEnvelope

Represents routable execution work.

Suggested fields:
- `job_id`
- `event: InboundEvent`
- `handler_name: str | None`
- `routing_key: str | None`
- `correlation_id`
- `causation_id | None`
- `attempt`
- `scheduled_at`
- `metadata`

This model allows the same work contract to be used for in-process execution and future external workers.

### 7.4 ExecutionContext

Represents the typed context given to handlers.

Suggested responsibilities:
- expose the current event
- expose correlation and runtime metadata
- expose state store, cache, and logger references through ports
- avoid leaking infrastructure specifics

### 7.5 HandlerResult

Represents the structured output of handler execution.

Suggested fields:
- `commands: list[OutboundCommand]`
- `state_writes: list[StateWrite]`
- `cache_writes: list[CacheWrite]`
- `logs: list[LogEntry]`

The exact shape may evolve, but the principle remains: handlers return intent, and the orchestrator applies effects.

## 8. Port contracts

Ports should use explicit ABCs or protocols where appropriate, with strong type hints and clear async boundaries.

### 8.1 BaseTrigger

Role:
- listen to an external source
- normalize input into `InboundEvent`
- submit the event to the runtime-facing ingress contract

Conceptual contract:
- `async start(publisher: EventPublisher) -> None`
- `async stop() -> None`

The trigger should not contain business logic or infrastructure-specific downstream decisions beyond optional routing hints.

### 8.2 BaseAction

Role:
- execute a supported `OutboundCommand`

Conceptual contract:
- `def supports(command: OutboundCommand) -> bool`
- `async execute(command: OutboundCommand) -> None`

### 8.3 QueuePort

Role:
- transport `JobEnvelope` units

Conceptual contract:
- `async publish(job: JobEnvelope) -> None`
- `async consume() -> JobEnvelope`
- `async ack(job: JobEnvelope) -> None`
- `async nack(job: JobEnvelope, reason: str | None = None) -> None`

Even in memory, explicit ack and nack semantics are retained because they are architecturally important and align the simple mode with future broker-backed adapters.

### 8.4 ExecutionStrategyPort

Role:
- define how jobs are executed after entering the queue

Conceptual contract:
- `async start(queue: QueuePort, orchestrator: Orchestrator) -> None`
- `async stop() -> None`

The execution strategy does not own domain logic. It owns topology and concurrency behavior.

### 8.5 CachePort

Role:
- provide ephemeral storage

Conceptual contract:
- `async get(key: str) -> object | None`
- `async set(key: str, value: object, ttl: int | None = None) -> None`
- `async delete(key: str) -> None`

### 8.6 StateStorePort

Role:
- provide durable storage for long-lived state

Conceptual contract:
- `async load(namespace: str, key: str) -> dict[str, object] | None`
- `async save(namespace: str, key: str, value: dict[str, object]) -> None`
- `async delete(namespace: str, key: str) -> None`

The core should not include rich querying in the MVP. That can be added later if it becomes a real requirement.

### 8.7 LoggerPort

Role:
- provide structured, replaceable observability

Conceptual contract:
- `async debug(message: str, **context: object) -> None`
- `async info(message: str, **context: object) -> None`
- `async warning(message: str, **context: object) -> None`
- `async error(message: str, **context: object) -> None`
- `async exception(message: str, **context: object) -> None`

## 9. Handler model

Handlers are not ports. They are typed application-level callables registered in a handler registry.

Reasoning:
- ports are reserved for framework boundaries
- handlers hold business logic
- keeping handlers out of the port layer preserves the boundary between domain behavior and infrastructure seams

MVP handler resolution model:
- use `handler_name` when explicitly provided by the trigger or dispatcher
- otherwise resolve by `event.name`

## 10. Constructor-based composition

Nexaroute uses explicit constructor injection instead of fluent builder chaining.

A target composition style for the MVP is:

```python
runtime = DispatcherRuntime(
    queue=InMemoryQueueAdapter(),
    execution=InMemoryExecutionAdapter(concurrency=100),
    orchestrator=Orchestrator(
        state_store=InMemoryStateStoreAdapter(),
        cache=InMemoryCacheAdapter(),
        logger=RichLoggerAdapter(),
        actions=[discord_action],
        handlers=handler_registry,
    ),
    triggers=[neonize_trigger],
    logger=RichLoggerAdapter(),
)
```

A thinner `Application` facade may be provided later if it adds value, but the internal design should remain constructor-driven and explicit.

## 11. MVP topology

The MVP uses the simple bootstrap model.

### 11.1 Included in the MVP

- single-process runtime
- in-memory queue
- in-memory execution strategy
- `asyncio.TaskGroup` for structured concurrency
- constructor-based composition
- strong type hints across the codebase
- Pydantic v2 models for value objects and transport-safe structures
- documentation and specs as first-class artifacts

### 11.2 Deferred beyond the MVP

- broker-backed production topology
- external workers as the default execution model
- retry policies
- dead-letter queues
- idempotency stores
- scheduling framework beyond a trigger abstraction
- richer query interfaces in the state port

## 12. Adapter toolbox

The architecture must demonstrate how robust tools fit as replaceable adapters.

### 12.1 In-memory adapters

Purpose:
- provide the raw, simple implementation
- make local development and MVP delivery frictionless

Included adapters:
- `InMemoryQueueAdapter`
- `InMemoryExecutionAdapter`
- `InMemoryCacheAdapter`
- `InMemoryStateStoreAdapter`
- `RichLoggerAdapter` or a minimal in-memory-friendly logger adapter

### 12.2 NeonizeTrigger

Purpose:
- wrap Neonize event listening
- transform WhatsApp events into `InboundEvent`
- submit events to the runtime without embedding business logic

### 12.3 DiscordAction

Purpose:
- translate `OutboundCommand` instances into Discord operations
- keep Discord integration entirely outside the core

### 12.4 TaskIQQueueAdapter

Purpose:
- implement `QueuePort`
- back the queue with TaskIQ and RabbitMQ
- serialize and deserialize `JobEnvelope`
- preserve ack and nack semantics as closely as the broker model allows

### 12.5 TaskIQExecutionAdapter

Purpose:
- implement `ExecutionStrategyPort`
- support externalized or broker-backed execution topologies when needed

### 12.6 RedisCacheAdapter

Purpose:
- implement `CachePort`
- support TTL-based ephemeral storage
- remain usable for future deduplication or idempotency mechanisms without changing the core

### 12.7 SQLAlchemyStateAdapter

Purpose:
- implement `StateStorePort`
- persist durable state with async SQLAlchemy and PostgreSQL
- isolate sessions, ORM models, and serialization inside the adapter layer

### 12.8 RichLoggerAdapter

Purpose:
- implement `LoggerPort`
- provide high-quality terminal output, readable tracebacks, and better operator experience

## 13. Example use cases supported by this model

### 13.1 Messaging trigger and dispatch

A Neonize-backed process or any bot process emits normalized events into Nexaroute. The Nexaroute runtime stays active, receives the event, dispatches a job, and continues listening. Handler processing occurs through the configured execution strategy without blocking ingress.

### 13.2 Periodic analytics and fan-out

A scheduled trigger emits a periodic event every three hours. A handler loads previously persisted messages, runs analysis, and emits commands to multiple action adapters such as Discord, Slack, WhatsApp, email, or mobile notifications. The same architecture supports one destination or many destinations with no change to the core.

## 14. Documentation strategy

Nexaroute is developed through spec-driven development.

### 14.1 Required documentation artifacts

- architecture overview
- runtime model
- ports and adapters reference
- lightweight ADRs for major structural decisions
- guides for triggers, handlers, actions, and bootstrap modes
- implementation plans derived from the approved spec

### 14.2 Documentation rules

- every important architectural choice must be written down
- the spec is the source of truth for the initial implementation plan
- implementation should not outrun documented decisions
- documentation must be clear, polished, and intentionally structured

## 15. Testing strategy

The test pyramid for the project should include:

- **unit tests** for domain models, registry behavior, and orchestration logic
- **contract tests** for adapter conformance against ports
- **integration tests** for simple bootstrap flows and selected real adapters

The MVP should prioritize confidence in:
- event normalization
- dispatch behavior
- handler resolution
- effect application order
- graceful runtime lifecycle

## 16. Design decisions summary

- Nexaroute is a hexagonal, event-oriented framework with an autonomous runtime.
- The runtime always listens for triggers and dispatches work without blocking ingress.
- Queue transport and execution topology are separate concerns.
- Worker separation is optional, not mandatory.
- The MVP defaults to in-process asynchronous execution with `asyncio.TaskGroup`.
- Constructor injection is preferred over fluent builder APIs.
- Strong type hints and Pydantic v2 models are foundational.
- External technologies are adapters only.
- Documentation and specs are core deliverables.

## 17. Next step

The next step after this approved design is to create a detailed implementation plan derived from this spec. That plan should break the framework into small, reviewable implementation steps while preserving the architecture defined here.
