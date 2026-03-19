"""Module contracts and abstract interfaces."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.types import CommandSpec, EventSpec, JobSpec, Role

if TYPE_CHECKING:
    from core.dependency_registry import DependencyRegistry
    from core.env import Settings
    from core.event_bus import EventBus


class InteractionContext(ABC):
    """Abstract context passed to command handlers — transport-agnostic."""

    @property
    @abstractmethod
    def user_id(self) -> int: ...

    @property
    @abstractmethod
    def user_role(self) -> Role: ...

    @property
    @abstractmethod
    def command(self) -> str: ...

    @property
    @abstractmethod
    def args(self) -> list[str]: ...

    @abstractmethod
    async def reply(self, text: str, parse_mode: str = "HTML") -> None: ...


class ModuleContext:
    """Context provided to modules during creation."""

    def __init__(
        self,
        logger: logging.Logger,
        event_bus: EventBus,
        settings: Settings,
        deps: DependencyRegistry,
        module_name: str,
    ):
        self.logger = logger
        self.event_bus = event_bus
        self.settings = settings
        self.deps = deps
        self.module_name = module_name

    @property
    def config(self) -> dict[str, str]:
        """Module-specific env vars (prefixed with MODULE_NAME_)."""
        return self.settings.module_config(self.module_name)


class FluxModule(ABC):
    """Base class for all FluxBuddy feature modules."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def commands(self) -> list[CommandSpec]:
        return []

    @property
    def event_listeners(self) -> list[EventSpec]:
        return []

    @property
    def jobs(self) -> list[JobSpec]:
        return []

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass
