from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from nexaroute.core.domain.events import InboundEvent


class JobEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    job_id: str = Field(default_factory=lambda: str(uuid4()))
    event: InboundEvent
    handler_name: str | None = None
    routing_key: str | None = None
    correlation_id: str
    causation_id: str | None = None
    attempt: int = 1
    scheduled_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_event(cls, event: InboundEvent) -> "JobEnvelope":
        return cls(
            event=event,
            handler_name=event.handler_name,
            correlation_id=event.correlation_id or event.id,
            causation_id=event.causation_id,
        )
