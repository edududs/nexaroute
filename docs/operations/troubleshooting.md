# Troubleshooting

## Runtime Starts But No Jobs Are Processed

Check:

- trigger actually publishes events
- queue consume loop is running
- handler name resolution matches registered key

## `LookupError: no action registered for target ...`

Cause: handler emitted command with `target` not supported by any action.

Fix:

- register the corresponding `BaseAction`
- or change command target to existing action contract

## Serialization Errors On Queue Adapters

Symptom:

- errors for `mappingproxy`, `datetime`, or non-JSON objects

Cause:

- frozen domain models and rich payload objects require conversion in adapter boundary

Fix:

- convert mapping-like objects to plain dict/list
- normalize date/time values to ISO-8601 strings

## Graceful Shutdown Raises Exception

Nexaroute surfaces cleanup failures by design.

Action:

- inspect trigger/strategy `stop()` implementations
- make stop idempotent
- ensure partial-stop retries are safe

## Event Parsed But Ignored

Common causes:

- parser returned `None`
- validation failed in handler input model
- handler returned empty effects by guard logic
