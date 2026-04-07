from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def freeze_mapping(value: Mapping[str, Any] | dict[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


class InboundEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    source: str
    payload: Mapping[str, Any] = Field(default_factory=dict)
    metadata: Mapping[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None
    causation_id: str | None = None
    handler_name: str | None = None

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "payload", freeze_mapping(self.payload))
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))

        if self.correlation_id is None:
            object.__setattr__(self, "correlation_id", self.id)
