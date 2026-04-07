from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from nexaroute.core.domain.events import InboundEvent, freeze_mapping

if TYPE_CHECKING:
    from nexaroute.core.ports.cache import CachePort
    from nexaroute.core.ports.logger import LoggerPort
    from nexaroute.core.ports.state_store import StateStorePort


@dataclass(slots=True, frozen=True)
class ExecutionContext:
    event: InboundEvent
    correlation_id: str
    state_store: "StateStorePort"
    cache: "CachePort"
    logger: "LoggerPort"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))
