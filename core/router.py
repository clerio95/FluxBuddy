"""Command routing with latency tracking and duplicate detection."""

from __future__ import annotations

import logging
import time
from typing import Any

from core.exceptions import DuplicateCommandError
from core.types import CommandSpec, role_has_access


class Router:
    """Registers commands from modules and dispatches them safely."""

    def __init__(self, logger: logging.Logger, event_bus: Any):
        self._logger = logger
        self._event_bus = event_bus
        self._commands: dict[str, tuple[CommandSpec, str]] = {}

    def register(self, spec: CommandSpec, module_name: str) -> None:
        if spec.name in self._commands:
            existing = self._commands[spec.name][1]
            raise DuplicateCommandError(
                f"Command '/{spec.name}' already registered by module '{existing}'"
            )
        self._commands[spec.name] = (spec, module_name)
        self._logger.info(
            f"action=command.registered | command={spec.name} "
            f"| module={module_name} | min_role={spec.min_role.value}"
        )

    async def dispatch(self, command_name: str, ctx: Any) -> None:
        entry = self._commands.get(command_name)
        if not entry:
            self._logger.warning(f"action=command.not_found | command={command_name}")
            return

        spec, module_name = entry
        user_role = ctx.user_role

        if not role_has_access(user_role, spec.min_role):
            self._logger.warning(
                f"action=command.unauthorized | command={command_name} "
                f"| user_id={ctx.user_id} | role={user_role.value}"
            )
            return

        start = time.perf_counter()
        try:
            await spec.handler(ctx)
            latency_ms = (time.perf_counter() - start) * 1000
            self._logger.info(
                f"action=command.completed | command={command_name} "
                f"| module={module_name} | user_id={ctx.user_id} "
                f"| role={user_role.value} | latency_ms={latency_ms:.1f}"
            )
            await self._event_bus.publish("command.completed", {
                "command": command_name,
                "module": module_name,
                "user_id": ctx.user_id,
                "latency_ms": latency_ms,
            })
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            self._logger.error(
                f"action=command.failed | command={command_name} "
                f"| module={module_name} | user_id={ctx.user_id} "
                f"| error={exc} | latency_ms={latency_ms:.1f}"
            )
            await self._event_bus.publish("command.failed", {
                "command": command_name,
                "module": module_name,
                "user_id": ctx.user_id,
                "error": str(exc),
            })

    @property
    def commands(self) -> dict[str, CommandSpec]:
        return {name: spec for name, (spec, _) in self._commands.items()}

    @property
    def command_modules(self) -> dict[str, str]:
        return {name: mod for name, (_, mod) in self._commands.items()}
