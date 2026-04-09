## InboundEvent

`InboundEvent` is the normalized ingress model.

### Fields
- `id`
- `name`
- `source`
- `payload`
- `metadata`
- `occurred_at`
- `correlation_id`
- `causation_id`
- `handler_name`

`handler_name` exists so a trigger may route directly to a registered handler when needed.
