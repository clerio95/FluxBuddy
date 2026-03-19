"""Lightweight internal event bus with error isolation per listener."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    """Async publish/subscribe bus — listener failures never propagate."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._listeners: dict[str, list[tuple[str, EventHandler]]] = {}

    def subscribe(self, event_name: str, handler: EventHandler, owner: str = "core") -> None:
        self._listeners.setdefault(event_name, []).append((owner, handler))
        self._logger.info(
            f"action=event.subscribed | event={event_name} | owner={owner}"
        )

    async def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        payload = payload or {}
        listeners = self._listeners.get(event_name, [])
        for owner, handler in listeners:
            try:
                await handler(payload)
            except Exception as exc:
                self._logger.error(
                    f"action=event.listener_error | event={event_name} "
                    f"| owner={owner} | error={exc}"
                )

    @property
    def subscriptions(self) -> dict[str, list[str]]:
        return {
            event: [owner for owner, _ in handlers]
            for event, handlers in self._listeners.items()
        }
