# FAQ

## Is Nexaroute a full workflow engine?

Not in the current MVP. It is an orchestration framework with explicit contracts and composable runtime pieces.

## Why return `HandlerResult` instead of executing everything inside handlers?

It keeps business logic testable and infrastructure-agnostic. Side effects are declared, then applied by orchestrator/adapters.

## Can I use Kafka/SQS/Rabbit instead of in-memory queue?

Yes. Implement `QueuePort` and provide your adapter in runtime composition.

## Can I run multiple handlers for one event?

Yes, by emitting fan-out commands or by publishing follow-up events depending on your design.

## Is this suitable for real-time messaging bots?

Yes. Model inbound messages as events and outbound replies as commands/actions. See `docs/guides/neonize-integration.md`.

## Does Nexaroute enforce exactly-once processing?

No. Exactly-once semantics depend on adapter and infrastructure strategy. Design for idempotency.
