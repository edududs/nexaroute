# Handler Patterns

## Pattern 1: Stateless Transform

Use when input event can be transformed directly into a command.

- minimal reads
- predictable latency
- easy to test

## Pattern 2: Read-Decide-Write

Use when decisions depend on current state.

1. read from `state_store`/`cache`
2. compute new state
3. emit `StateWrite`/`CacheWrite`
4. optionally emit commands

## Pattern 3: Log-Only Guard

Use for unsupported or invalid events.

- return `HandlerResult(logs=(...))`
- avoid throwing for expected business-level rejections

## Pattern 4: Fan-Out Commands

When one event must trigger multiple integrations:

- emit multiple `OutboundCommand` entries
- use independent `BaseAction` implementations by `target`

## Anti-Patterns

- direct DB/network calls inside handlers
- broad `try/except Exception` in handlers that hides business failures
- mutable shared global state inside adapters/handlers
