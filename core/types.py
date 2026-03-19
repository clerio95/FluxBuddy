"""Core type definitions for FluxBuddy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable


class Role(Enum):
    NONE = "none"
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


ROLE_HIERARCHY: dict[Role, int] = {
    Role.NONE: 0,
    Role.VIEWER: 1,
    Role.OPERATOR: 2,
    Role.ADMIN: 3,
}


def role_has_access(user_role: Role, min_role: Role) -> bool:
    """Check if a user role meets the minimum required role."""
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[min_role]


@dataclass(frozen=True)
class CommandSpec:
    """Declares a command owned by a module."""
    name: str
    description: str
    min_role: Role
    handler: Callable[..., Awaitable[None]]


@dataclass(frozen=True)
class EventSpec:
    """Declares an event listener owned by a module."""
    event_name: str
    handler: Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(frozen=True)
class JobSpec:
    """Declares a scheduled job owned by a module."""
    name: str
    handler: Callable[..., Awaitable[None]]
    interval_seconds: int | None = None
    daily_time: tuple[int, int] | None = None  # (hour, minute)
    days: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6)


@dataclass(frozen=True)
class ModuleManifest:
    """Parsed plugin.json metadata."""
    name: str
    version: str
    enabled: bool
    entrypoint: str
