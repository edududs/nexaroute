from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from nexaroute.application.registry import HandlerRegistry
from nexaroute.core.domain.commands import OutboundCommand
from nexaroute.core.domain.context import ExecutionContext
from nexaroute.core.domain.jobs import JobEnvelope
from nexaroute.core.domain.results import HandlerResult, LogEntry
from nexaroute.core.ports.actions import BaseAction
from nexaroute.core.ports.cache import CachePort
from nexaroute.core.ports.execution import ExecutionProcessorPort
from nexaroute.core.ports.logger import LoggerPort
from nexaroute.core.ports.state_store import StateStorePort


class Orchestrator(ExecutionProcessorPort):
    def __init__(
        self,
        *,
        handlers: HandlerRegistry,
        state_store: StateStorePort,
        cache: CachePort,
        logger: LoggerPort,
        actions: Sequence[BaseAction],
    ) -> None:
        self.handlers = handlers
        self.state_store = state_store
        self.cache = cache
        self.logger = logger
        self.actions = list(actions)

    async def process(self, job: JobEnvelope) -> None:
        handler_key = job.handler_name or job.event.name
        handler = self.handlers.resolve(handler_key)
        context = ExecutionContext(
            event=job.event,
            correlation_id=job.correlation_id,
            state_store=self.state_store,
            cache=self.cache,
            logger=self.logger,
            metadata=job.metadata,
        )
        result = await handler(context)
        await self._apply(result)
        await self.logger.info("job processed", job_id=job.job_id, handler=handler_key)

    async def _apply(self, result: HandlerResult) -> None:
        for write in result.state_writes:
            await self.state_store.save(write.namespace, write.key, self._thaw_mapping(write.value))

        for write in result.cache_writes:
            await self.cache.set(write.key, self._thaw_mapping(write.value), ttl=write.ttl)

        for command in result.commands:
            action = self._resolve_action(command)
            await action.execute(command)

        for entry in result.logs:
            await self._log_entry(entry)

    def _resolve_action(self, command: OutboundCommand) -> BaseAction:
        for action in self.actions:
            if action.supports(command):
                return action
        raise LookupError(f"no action registered for target '{command.target}'")

    def _thaw_mapping(self, value: Mapping[str, Any]) -> dict[str, Any]:
        thawed: dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(item, Mapping):
                thawed[key] = self._thaw_mapping(item)
            elif isinstance(item, tuple):
                thawed[key] = [self._thaw_sequence_item(element) for element in item]
            else:
                thawed[key] = item
        return thawed

    def _thaw_sequence_item(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return self._thaw_mapping(value)
        if isinstance(value, tuple):
            return [self._thaw_sequence_item(item) for item in value]
        return value

    async def _log_entry(self, entry: LogEntry) -> None:
        if entry.level == "debug":
            await self.logger.debug(entry.message, **entry.context)
        elif entry.level == "info":
            await self.logger.info(entry.message, **entry.context)
        elif entry.level == "warning":
            await self.logger.warning(entry.message, **entry.context)
        else:
            await self.logger.error(entry.message, **entry.context)
