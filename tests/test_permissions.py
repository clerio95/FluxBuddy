from core.env import Settings
from core.permissions import PermissionService
from core.types import Role
from zoneinfo import ZoneInfo


def _settings() -> Settings:
    return Settings(
        bot_token="x",
        group_chat_id=None,
        admin_user_ids=[1],
        operator_user_ids=[2],
        viewer_user_ids=[3],
        default_role="none",
        log_max_bytes=100,
        log_file="logs/test.log",
        timezone=ZoneInfo("America/Sao_Paulo"),
    )


def test_permission_roles_and_authorization():
    perms = PermissionService(_settings())

    assert perms.resolve_role(1) is Role.ADMIN
    assert perms.resolve_role(2) is Role.OPERATOR
    assert perms.resolve_role(3) is Role.VIEWER
    assert perms.resolve_role(999) is Role.NONE

    assert perms.is_authorized(1, Role.ADMIN)
    assert perms.is_authorized(2, Role.VIEWER)
    assert not perms.is_authorized(999, Role.VIEWER)
