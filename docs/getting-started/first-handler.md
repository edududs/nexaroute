# First Useful Handler

A handler receives `ExecutionContext` and returns `HandlerResult`.

```python
from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import CacheWrite, HandlerResult, LogEntry, StateWrite


async def persist_and_emit(ctx: ExecutionContext) -> HandlerResult:
    user_id = str(ctx.event.payload.get("user_id", "unknown"))

    return HandlerResult(
        state_writes=(
            StateWrite(
                namespace="users",
                key=user_id,
                value={"last_event": ctx.event.name},
            ),
        ),
        cache_writes=(
            CacheWrite(
                key=f"user:{user_id}:last_event",
                value={"event": ctx.event.name},
                ttl=60,
            ),
        ),
        commands=(
            OutboundCommand(
                name="notify-user",
                target="notifications.email",
                payload={"user_id": user_id, "event": ctx.event.name},
            ),
        ),
        logs=(
            LogEntry(
                level="info",
                message="processed user event",
                context={"user_id": user_id},
            ),
        ),
    )
```

## Rule Of Thumb

- Keep handlers focused on business decisions.
- Keep infrastructure concerns in actions and adapters.
