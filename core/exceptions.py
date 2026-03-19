"""Custom exceptions for FluxBuddy core."""


class FluxBuddyError(Exception):
    """Base exception for all FluxBuddy errors."""


class ModuleLoadError(FluxBuddyError):
    """A module failed to load."""


class DuplicateCommandError(FluxBuddyError):
    """Two modules tried to register the same command."""


class AuthorizationError(FluxBuddyError):
    """User lacks the required permission level."""
