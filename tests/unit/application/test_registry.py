import pytest

from nexaroute.application.registry import HandlerRegistry
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.results import HandlerResult


async def sample_handler(_: ExecutionContext) -> HandlerResult:
    return HandlerResult()


def test_registry_resolves_registered_handler() -> None:
    registry = HandlerRegistry()
    registry.register("message.received", sample_handler)

    assert registry.resolve("message.received") is sample_handler


def test_registry_raises_for_missing_handler() -> None:
    registry = HandlerRegistry()

    with pytest.raises(KeyError):
        registry.resolve("missing")
