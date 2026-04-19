# `QueuePort`

`QueuePort` defines the transport contract for `JobEnvelope`.

## Methods

- `publish(job)`: enqueue work
- `consume()`: fetch next available job
- `ack(job)`: confirm successful processing
- `nack(job, reason=None)`: reject job and communicate failure context

## Design Intent

`QueuePort` is explicit about acknowledgement semantics so execution strategy can implement backpressure and failure behavior without coupling to a concrete broker.

## Adapter Requirements

- preserve `JobEnvelope` integrity
- keep `ack/nack` idempotent
- handle consumer shutdown safely
- make retry policy explicit (`nack` behavior should be documented)

## MVP Adapter

`InMemoryQueueAdapter` uses `asyncio.Queue` and tracks in-flight jobs to emulate ack/nack flow for local development and tests.
