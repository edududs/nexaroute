from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from nexaroute.core.domain.events import InboundEvent, freeze_mapping, normalize_utc_datetime


class JobEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    job_id: str = Field(default_factory=lambda: str(uuid4()))
    event: InboundEvent
    handler_name: str | None = None
    routing_key: str | None = None
    correlation_id: str
    causation_id: str | None = None
    attempt: int = Field(default=1, ge=1)
    scheduled_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: Mapping[str, Any] = Field(default_factory=dict)

    @field_validator("scheduled_at", mode="after")
    @classmethod
    def ensure_scheduled_at_is_utc(cls, value: AwareDatetime) -> datetime:
        return normalize_utc_datetime(value)

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))

    @classmethod
    def from_event(cls, event: InboundEvent) -> "JobEnvelope":
        return cls(
            event=event,
            handler_name=event.handler_name,
            correlation_id=event.correlation_id or event.id,
            causation_id=event.id,
        )
