"""Authorization and role resolution."""

from core.env import Settings
from core.types import Role, role_has_access


class PermissionService:
    """Resolves user roles and enforces access checks."""

    def __init__(self, settings: Settings):
        self._admins = set(settings.admin_user_ids)
        self._operators = set(settings.operator_user_ids)
        self._viewers = set(settings.viewer_user_ids)
        self._default = settings.default_role

    def resolve_role(self, user_id: int) -> Role:
        if user_id in self._admins:
            return Role.ADMIN
        if user_id in self._operators:
            return Role.OPERATOR
        if user_id in self._viewers:
            return Role.VIEWER
        if self._default == "viewer":
            return Role.VIEWER
        return Role.NONE

    def is_authorized(self, user_id: int, min_role: Role = Role.VIEWER) -> bool:
        return role_has_access(self.resolve_role(user_id), min_role)
