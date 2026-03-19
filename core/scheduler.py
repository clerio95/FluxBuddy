"""Scheduled job management with error isolation."""

from __future__ import annotations

import logging
import time
from typing import Any

from core.types import JobSpec


class Scheduler:
    """Registers jobs from modules and executes them safely."""

    def __init__(self, logger: logging.Logger, event_bus: Any):
        self._logger = logger
        self._event_bus = event_bus
        self._jobs: list[tuple[JobSpec, str]] = []

    def register(self, spec: JobSpec, module_name: str) -> None:
        self._jobs.append((spec, module_name))
        if spec.interval_seconds:
            schedule_desc = f"every {spec.interval_seconds}s"
        elif spec.daily_time:
            schedule_desc = f"daily at {spec.daily_time[0]:02d}:{spec.daily_time[1]:02d}"
        else:
            schedule_desc = "unknown schedule"
        self._logger.info(
            f"action=job.registered | job={spec.name} "
            f"| module={module_name} | schedule={schedule_desc}"
        )

    async def execute_job(self, spec: JobSpec, module_name: str, *args: Any, **kwargs: Any) -> None:
        start = time.perf_counter()
        try:
            await spec.handler(*args, **kwargs)
            latency_ms = (time.perf_counter() - start) * 1000
            self._logger.info(
                f"action=job.completed | job={spec.name} "
                f"| module={module_name} | latency_ms={latency_ms:.1f}"
            )
            await self._event_bus.publish("job.completed", {
                "job": spec.name,
                "module": module_name,
                "latency_ms": latency_ms,
            })
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            self._logger.error(
                f"action=job.failed | job={spec.name} "
                f"| module={module_name} | error={exc} | latency_ms={latency_ms:.1f}"
            )
            await self._event_bus.publish("job.failed", {
                "job": spec.name,
                "module": module_name,
                "error": str(exc),
            })

    @property
    def jobs(self) -> list[tuple[JobSpec, str]]:
        return list(self._jobs)
