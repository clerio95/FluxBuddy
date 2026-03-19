import logging

import pytest

from core.event_bus import EventBus


@pytest.mark.asyncio
async def test_event_bus_isolates_listener_errors():
    logger = logging.getLogger("test.event_bus")
    bus = EventBus(logger)
    calls = []

    async def bad_listener(payload):
        raise RuntimeError("boom")

    async def good_listener(payload):
        calls.append(payload["ok"])

    bus.subscribe("test.event", bad_listener, owner="bad")
    bus.subscribe("test.event", good_listener, owner="good")

    await bus.publish("test.event", {"ok": True})

    assert calls == [True]
