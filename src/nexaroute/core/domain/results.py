from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.events import freeze_mapping

LogLevel = Literal["debug", "info", "warning", "error"]


class StateWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    namespace: str
    key: str
    value: Mapping[str, Any]

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "value", freeze_mapping(self.value))


class CacheWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str
    value: Mapping[str, Any]
    ttl: int | None = None

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "value", freeze_mapping(self.value))


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level: LogLevel
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: Mapping[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "context", freeze_mapping(self.context))


class HandlerResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    commands: tuple[OutboundCommand, ...] = Field(default_factory=tuple)
    state_writes: tuple[StateWrite, ...] = Field(default_factory=tuple)
    cache_writes: tuple[CacheWrite, ...] = Field(default_factory=tuple)
    logs: tuple[LogEntry, ...] = Field(default_factory=tuple)
