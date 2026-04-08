# Nexaroute

Nexaroute is an async, event-oriented automation and orchestration framework built on Hexagonal Architecture.

## MVP scope

- autonomous runtime
- typed domain models
- strict ports
- in-memory queue and execution strategy
- constructor-based dependency injection

## Quick start

```python
from nexaroute.application.bootstrap import create_simple_runtime

runtime = create_simple_runtime(
    triggers=[],
    handlers={},
)
```

See `docs/architecture/overview.md` and `docs/guides/bootstrap-simple.md` for details.
