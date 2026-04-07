from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from nexaroute.core.domain.events import freeze_mapping, normalize_utc_datetime


class OutboundCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    target: str
    payload: Mapping[str, Any] = Field(default_factory=dict)
    metadata: Mapping[str, Any] = Field(default_factory=dict)
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_created_at_is_utc(cls, value: AwareDatetime) -> datetime:
        return normalize_utc_datetime(value)

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "payload", freeze_mapping(self.payload))
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))

        if self.correlation_id is None:
            object.__setattr__(self, "correlation_id", self.id)
