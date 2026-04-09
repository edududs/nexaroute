from abc import ABC

from nexaroute.core.ports.actions import BaseAction
from nexaroute.core.ports.cache import CachePort
from nexaroute.core.ports.execution import ExecutionProcessorPort, ExecutionStrategyPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.queue import QueuePort
from nexaroute.core.ports.state_store import StateStorePort
from nexaroute.core.ports.triggers import BaseTrigger


def test_ports_are_abstract_base_classes() -> None:
    for port in (BaseTrigger, BaseAction, QueuePort, ExecutionProcessorPort, ExecutionStrategyPort, CachePort, StateStorePort, LoggerPort):
        assert issubclass(port, ABC)
        assert bool(getattr(port, "__abstractmethods__"))
