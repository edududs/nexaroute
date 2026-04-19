# `InboundEvent`

`InboundEvent` is the canonical ingress model for Nexaroute.

## Purpose

- represent an incoming business signal in a transport-agnostic form
- preserve traceability across pipelines
- keep payload immutable after publication

## Fields

- `id`: event identifier
- `name`: semantic event name (for handler resolution)
- `source`: producer identity (service, trigger, adapter)
- `payload`: business payload
- `metadata`: technical metadata
- `occurred_at`: event timestamp (UTC-normalized)
- `correlation_id`: request/flow correlation
- `causation_id`: parent event id
- `handler_name`: optional explicit handler override

## Behavioral Notes

- model is frozen (`frozen=True`)
- nested mappings and sequences are frozen in `model_post_init`
- if `correlation_id` is omitted, it defaults to `id`

## Routing

By default, orchestrator resolves handler by `event.name`.  
When `handler_name` is set, it can route directly to a specific registered handler.
