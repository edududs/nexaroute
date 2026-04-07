from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexaroute.core.domain.commands import OutboundCommand

LogLevel = Literal["debug", "info", "warning", "error"]


class StateWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    namespace: str
    key: str
    value: dict[str, Any]


class CacheWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str
    value: dict[str, Any]
    ttl: int | None = None


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level: LogLevel
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: dict[str, Any] = Field(default_factory=dict)


class HandlerResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    commands: list[OutboundCommand] = Field(default_factory=list)
    state_writes: list[StateWrite] = Field(default_factory=list)
    cache_writes: list[CacheWrite] = Field(default_factory=list)
    logs: list[LogEntry] = Field(default_factory=list)
