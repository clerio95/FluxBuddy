#!/usr/bin/env python3
"""FluxBuddy — Modular workflow bot core."""

import asyncio
import sys


def main() -> None:
    from core.bootstrap import bootstrap
    from transports.telegram.adapter import TelegramTransport

    result = bootstrap()

    transport = TelegramTransport(
        settings=result.settings,
        router=result.router,
        scheduler=result.scheduler,
        perms=result.permissions,
        logger=result.logger,
        event_bus=result.event_bus,
        modules=result.modules,
    )
    transport.run()


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
