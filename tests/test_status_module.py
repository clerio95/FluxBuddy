from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.contracts import FluxModule, InteractionContext, ModuleContext
from core.dependency_registry import DependencyRegistry
from core.env import Settings
from core.event_bus import EventBus
from core.logging import setup_logging
from modules.status.module import create_module


class DummyContext(InteractionContext):
    def __init__(self):
        self.messages = []

    @property
    def user_id(self) -> int:
        return 1

    @property
    def user_role(self):
        from core.types import Role
        return Role.ADMIN

    @property
    def command(self) -> str:
        return "status"

    @property
    def args(self) -> list[str]:
        return []

    async def reply(self, text: str, parse_mode: str = "HTML") -> None:
        self.messages.append(text)


@pytest.mark.asyncio
async def test_status_module_happy_path(tmp_path):
    settings = Settings(
        bot_token="x",
        group_chat_id=None,
        admin_user_ids=[1],
        operator_user_ids=[],
        viewer_user_ids=[],
        default_role="none",
        log_max_bytes=1000,
        log_file=str(tmp_path / "test.log"),
        timezone=ZoneInfo("America/Sao_Paulo"),
    )
    logger = setup_logging(settings.log_file, settings.log_max_bytes)
    event_bus = EventBus(logger)
    deps = DependencyRegistry()
    ctx = ModuleContext(logger, event_bus, settings, deps, "status")
    module = create_module(ctx)

    await module.on_startup()

    dummy = DummyContext()
    handler = module.commands[0].handler
    await handler(dummy)

    assert dummy.messages
    assert "STATUS" in dummy.messages[0]
