"""Application bootstrap — wires all components together."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from core.env import load_settings, Settings
from core.logging import setup_logging
from core.event_bus import EventBus
from core.router import Router
from core.scheduler import Scheduler
from core.permissions import PermissionService
from core.dependency_registry import DependencyRegistry
from core.plugin_loader import load_modules
from core.contracts import FluxModule


@dataclass
class BootstrapResult:
    settings: Settings
    logger: logging.Logger
    event_bus: EventBus
    router: Router
    scheduler: Scheduler
    permissions: PermissionService
    modules: list[FluxModule]


def bootstrap() -> BootstrapResult:
    """Load settings, wire components, discover modules, and return a ready context."""
    settings = load_settings()
    logger = setup_logging(settings.log_file, settings.log_max_bytes)

    logger.info("action=bootstrap.start")

    event_bus = EventBus(logger)
    deps = DependencyRegistry()
    perms = PermissionService(settings)
    router = Router(logger, event_bus)
    scheduler = Scheduler(logger, event_bus)

    deps.register("logger", logger)
    deps.register("event_bus", event_bus)
    deps.register("settings", settings)
    deps.register("permissions", perms)
    deps.register("router", router)
    deps.register("scheduler", scheduler)

    modules = load_modules(logger, event_bus, settings, deps)

    for mod in modules:
        for cmd in mod.commands:
            router.register(cmd, mod.name)
        for evt in mod.event_listeners:
            event_bus.subscribe(evt.event_name, evt.handler, mod.name)
        for job in mod.jobs:
            scheduler.register(job, mod.name)

    logger.info(
        f"action=bootstrap.complete | modules={len(modules)} "
        f"| commands={len(router.commands)} | jobs={len(scheduler.jobs)}"
    )

    return BootstrapResult(
        settings=settings,
        logger=logger,
        event_bus=event_bus,
        router=router,
        scheduler=scheduler,
        permissions=perms,
        modules=modules,
    )
