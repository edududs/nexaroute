## QueuePort

`QueuePort` transports `JobEnvelope` items.

### Methods
- `publish(job)`
- `consume()`
- `ack(job)`
- `nack(job, reason=None)`

In the MVP, `InMemoryQueueAdapter` implements this contract using `asyncio.Queue` plus explicit in-flight tracking.
