"""Telegram transport adapter — bridges python-telegram-bot to the FluxBuddy core."""

from __future__ import annotations

import logging
from datetime import time as dtime
from typing import Any

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.contracts import FluxModule, InteractionContext
from core.event_bus import EventBus
from core.permissions import PermissionService
from core.router import Router
from core.scheduler import Scheduler
from core.types import Role


class TelegramInteractionContext(InteractionContext):
    """Concrete InteractionContext backed by a Telegram Update."""

    def __init__(
        self,
        update: Update,
        tg_context: ContextTypes.DEFAULT_TYPE,
        command: str,
        perms: PermissionService,
    ):
        self._update = update
        self._tg_context = tg_context
        self._command = command
        self._perms = perms

    @property
    def user_id(self) -> int:
        return self._update.effective_user.id  # type: ignore[union-attr]

    @property
    def user_role(self) -> Role:
        return self._perms.resolve_role(self.user_id)

    @property
    def command(self) -> str:
        return self._command

    @property
    def args(self) -> list[str]:
        return list(self._tg_context.args or [])

    async def reply(self, text: str, parse_mode: str = "HTML") -> None:
        await self._update.message.reply_text(  # type: ignore[union-attr]
            text, parse_mode=parse_mode, disable_web_page_preview=True,
        )


class TelegramTransport:
    """Adapts FluxBuddy core to python-telegram-bot runtime."""

    def __init__(
        self,
        settings: Any,
        router: Router,
        scheduler: Scheduler,
        perms: PermissionService,
        logger: logging.Logger,
        event_bus: EventBus,
        modules: list[FluxModule],
    ):
        self._settings = settings
        self._router = router
        self._scheduler = scheduler
        self._perms = perms
        self._logger = logger
        self._event_bus = event_bus
        self._modules = modules
        self._app = Application.builder().token(settings.bot_token).build()

    # ── handler / job wrappers ──────────────────────────────────

    def _build_command_handler(self, cmd_name: str):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not update.effective_user or not update.message:
                return
            ctx = TelegramInteractionContext(update, context, cmd_name, self._perms)
            await self._router.dispatch(cmd_name, ctx)
        return handler

    def _build_job_wrapper(self, job_spec, module_name: str):
        async def wrapper(tg_context: ContextTypes.DEFAULT_TYPE):
            async def send_to_group(text: str, parse_mode: str = "HTML"):
                gid = self._settings.group_chat_id
                if gid:
                    await tg_context.bot.send_message(
                        chat_id=gid, text=text,
                        parse_mode=parse_mode, disable_web_page_preview=True,
                    )
            await self._scheduler.execute_job(job_spec, module_name, send_to_group)
        return wrapper

    # ── setup and run ───────────────────────────────────────────

    def _setup(self) -> None:
        for cmd_name in self._router.commands:
            self._app.add_handler(
                CommandHandler(cmd_name, self._build_command_handler(cmd_name))
            )

        jq = self._app.job_queue
        if jq:
            for job_spec, module_name in self._scheduler.jobs:
                wrapper = self._build_job_wrapper(job_spec, module_name)
                if job_spec.interval_seconds:
                    jq.run_repeating(
                        wrapper, interval=job_spec.interval_seconds, first=15,
                    )
                elif job_spec.daily_time:
                    h, m = job_spec.daily_time
                    jq.run_daily(
                        wrapper,
                        time=dtime(h, m, tzinfo=self._settings.timezone),
                        days=job_spec.days,
                    )

    def run(self) -> None:
        """Wire handlers, register bot commands, and start polling."""
        self._setup()

        modules = self._modules
        event_bus = self._event_bus
        logger = self._logger
        router_commands = self._router.commands

        async def post_init(app_: Application) -> None:
            bot_commands = [
                BotCommand(name, spec.description)
                for name, spec in router_commands.items()
            ]
            if bot_commands:
                await app_.bot.set_my_commands(bot_commands)

            for mod in modules:
                try:
                    await mod.on_startup()
                except Exception as exc:
                    logger.error(
                        f"action=module.startup_failed | module={mod.name} | error={exc}"
                    )

            await event_bus.publish("system.started")
            logger.info("action=app.started")

        async def post_shutdown(app_: Application) -> None:
            for mod in modules:
                try:
                    await mod.on_shutdown()
                except Exception as exc:
                    logger.error(
                        f"action=module.shutdown_failed | module={mod.name} | error={exc}"
                    )

            await event_bus.publish("system.stopped")
            logger.info("action=app.stopped")

        self._app.post_init = post_init
        self._app.post_shutdown = post_shutdown

        logger.info("action=transport.telegram.starting")
        self._app.run_polling(drop_pending_updates=True)
