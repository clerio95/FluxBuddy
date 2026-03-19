"""Status module — /status and /healthcheck commands."""

from __future__ import annotations

import platform
import sys
from datetime import datetime
from typing import Protocol, runtime_checkable

from core.contracts import FluxModule, InteractionContext, ModuleContext
from core.types import CommandSpec, Role

_START_TIME: datetime | None = None


@runtime_checkable
class _RouterLike(Protocol):
    @property
    def commands(self) -> dict: ...


@runtime_checkable
class _SchedulerLike(Protocol):
    @property
    def jobs(self) -> list: ...


class StatusModule(FluxModule):
    def __init__(self, ctx: ModuleContext):
        self._ctx = ctx

    @property
    def name(self) -> str:
        return "status"

    @property
    def commands(self) -> list[CommandSpec]:
        return [
            CommandSpec("status", "Bot status and uptime", Role.VIEWER, self._cmd_status),
            CommandSpec("healthcheck", "Health check (admin only)", Role.ADMIN, self._cmd_healthcheck),
        ]

    async def on_startup(self) -> None:
        global _START_TIME
        _START_TIME = datetime.now(self._ctx.settings.timezone)

    async def _cmd_status(self, ctx: InteractionContext) -> None:
        tz = self._ctx.settings.timezone
        now = datetime.now(tz)
        uptime = now - _START_TIME if _START_TIME else None

        if uptime:
            h, rem = divmod(int(uptime.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            uptime_str = f"{h:02d}:{m:02d}:{s:02d}"
        else:
            uptime_str = "unknown"

        text = (
            "⚙️ <b>STATUS — FluxBuddy</b>\n\n"
            f"🕐 Uptime: <code>{uptime_str}</code>\n"
            f"🐍 Python: <code>{sys.version.split()[0]}</code>\n"
            f"🖥️ OS: <code>{platform.system()} {platform.release()}</code>\n"
            f"⏰ Now: <code>{now.strftime('%Y-%m-%d %H:%M')}</code>\n"
        )
        await ctx.reply(text)

    async def _cmd_healthcheck(self, ctx: InteractionContext) -> None:
        deps = self._ctx.deps
        bus = self._ctx.event_bus
        router = deps.get("router")
        scheduler = deps.get("scheduler")

        n_commands = len(router.commands) if isinstance(router, _RouterLike) else "?"
        n_jobs = len(scheduler.jobs) if isinstance(scheduler, _SchedulerLike) else "?"
        n_subs = sum(len(v) for v in bus.subscriptions.values())

        text = (
            "🏥 <b>HEALTHCHECK</b>\n\n"
            f"📦 Registered deps: <code>{', '.join(deps.registered)}</code>\n"
            f"🔀 Commands: <code>{n_commands}</code>\n"
            f"⏱️ Jobs: <code>{n_jobs}</code>\n"
            f"📡 Event subscriptions: <code>{n_subs}</code>\n"
            f"✅ Core is healthy\n"
        )
        await ctx.reply(text)


def create_module(ctx: ModuleContext) -> FluxModule:
    return StatusModule(ctx)
