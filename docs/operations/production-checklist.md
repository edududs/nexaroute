# Production Checklist

Use this before shipping Nexaroute-backed services.

## Runtime And Queue

- [ ] Replace in-memory queue with durable transport.
- [ ] Define `ack/nack` semantics and dead-letter behavior.
- [ ] Configure worker concurrency limits per deployment.
- [ ] Add graceful shutdown timeout and drain policy.

## Reliability

- [ ] Define idempotency keys (event id/correlation id/business key).
- [ ] Add retry policy per failure class (transient vs permanent).
- [ ] Add poison message handling strategy.

## Observability

- [ ] Structured logs with `correlation_id`.
- [ ] Metrics: queue lag, processing latency, nack rate, command failures.
- [ ] Tracing across trigger -> handler -> action.

## Data And Cache

- [ ] Namespaced state keys with explicit ownership.
- [ ] TTL policy for cache keys.
- [ ] Schema migration/versioning strategy for state payloads.

## Security

- [ ] Secrets not stored in code.
- [ ] TLS/auth for queue/cache/database.
- [ ] Principle of least privilege for credentials.
