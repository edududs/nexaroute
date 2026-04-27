# Nexaroute

Nexaroute is an async-first framework for intelligent task and event routing.

It is being shaped to handle many inputs, many outputs, dynamic routing, and isolated handler execution without forcing the user into a single runtime or provider model.

## Current direction

Nexaroute is evolving into a package family with clear boundaries:

- `nexaroute-core`: the public low-level foundation for contracts, runtime primitives, routing, and execution boundaries
- `nexaroute`: the main package most developers should start with — the default armor, with ergonomic bootstrap and useful defaults
- role-oriented extensions such as scheduling, runtime hosting, ingress, outbound actions, observability, and execution backends

The framework is designed so that each piece can be useful on its own, while `nexaroute` delivers the easiest standard way to start.

## What Nexaroute is for

Nexaroute is meant for workflows where you need to:

- observe multiple sources at the same time
- normalize external signals into internal events or tasks
- route work to one handler, many handlers, or dynamically selected handlers
- isolate execution by strategy
- notify or act across one or many destinations concurrently

Examples of the model Nexaroute is targeting:

- a GitHub issue triggers notifications to WhatsApp, Slack, and Discord
- Telegram, internal webhooks, and other sources feed the same runtime
- one event is transformed into provider-specific actions for different destinations
- a trigger can target a specific handler or let the routing policies decide

## Core ideas

### 1. Role-oriented integrations

Nexaroute should think in architectural roles first, not provider names first.

A single external technology may participate as:

- a trigger or ingress source
- an outbound action or destination
- a runtime host
- a transversal adapter such as mapping, auth, rate limiting, or session support

That means a provider such as Telegram, Discord, GitHub, FastAPI, or WhatsApp can occupy more than one role at the same time.

### 2. Intelligent routing

Routing is a native concern of the framework.

An event or task may:

- target one handler explicitly
- target a known set of handlers
- be evaluated by routing policies
- fan out to multiple handlers or multiple outbound destinations

### 3. Isolated handler execution

Handlers are independent work units.

Nexaroute is being designed so each handler can run in its own execution lane, with future strategies such as:

- inline async execution
- isolated async tasks
- threads
- processes
- dedicated workers or consumers

### 4. Easy start, scalable growth

The goal is to make `nexaroute` easy to start with while preserving strong extensibility.

The intended model is:

- start with the default Nexaroute experience
- add or swap pieces as your workflow grows
- keep the core lightweight and strongly typed
- avoid rewriting your architecture when new integrations appear

## Current repository status

This repository currently contains the MVP foundation:

- async runtime
- typed domain models
- strict ports
- in-memory queue and execution strategy
- constructor-based dependency injection
- initial adapter and runtime composition patterns

This is still an early framework iteration. The long-term architecture direction is documented in:

- `docs/superpowers/specs/2026-04-27-nexaroute-core-extensible-design.md`

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
        await asyncio.sleep(1)
    finally:
        await runtime.stop()


asyncio.run(main())
```

## Documentation

Full documentation lives in `docs/README.md`.

Main tracks:

- getting started
- concepts
- architecture and reference
- guides
- operations
- FAQ

Primary entrypoint: `docs/README.md`.
