import pytest

from core.exceptions import DuplicateCommandError
from core.router import Router
from core.types import CommandSpec, Role


class DummyEventBus:
    async def publish(self, *args, **kwargs):
        return None


async def _handler(ctx):
    return None


def test_router_rejects_duplicate_commands():
    router = Router(logger=__import__("logging").getLogger("test.router"), event_bus=DummyEventBus())

    router.register(CommandSpec("status", "Status", Role.VIEWER, _handler), "status")

    with pytest.raises(DuplicateCommandError):
        router.register(CommandSpec("status", "Status", Role.VIEWER, _handler), "other")
