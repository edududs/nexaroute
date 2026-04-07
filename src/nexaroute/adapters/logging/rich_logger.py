from __future__ import annotations

from typing import Any

from rich.console import Console

from nexaroute.core.ports.logger import LoggerPort


class RichLoggerAdapter(LoggerPort):
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console(stderr=True)

    async def debug(self, message: str, **context: Any) -> None:
        self._console.log(f"[cyan]DEBUG[/cyan] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def info(self, message: str, **context: Any) -> None:
        self._console.log(f"[green]INFO[/green] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def warning(self, message: str, **context: Any) -> None:
        self._console.log(f"[yellow]WARN[/yellow] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def error(self, message: str, **context: Any) -> None:
        self._console.log(f"[red]ERROR[/red] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)

    async def exception(self, message: str, **context: Any) -> None:
        self._console.log(f"[bold red]EXCEPTION[/bold red] {message}", log_locals=False)
        if context:
            self._console.log(context, log_locals=False)
