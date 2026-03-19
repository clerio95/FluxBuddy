"""Environment and settings management."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv


@dataclass
class Settings:
    """Centralized application settings loaded from .env."""
    bot_token: str
    group_chat_id: int | None
    admin_user_ids: list[int]
    operator_user_ids: list[int]
    viewer_user_ids: list[int]
    default_role: str  # "none" or "viewer"
    log_max_bytes: int
    log_file: str
    timezone: ZoneInfo
    data_dir: str = "data"
    log_dir: str = "logs"

    def module_config(self, module_name: str) -> dict[str, str]:
        """Return env vars prefixed with MODULE_NAME_ as a lowercase dict."""
        prefix = module_name.upper() + "_"
        return {
            k[len(prefix):].lower(): v
            for k, v in os.environ.items()
            if k.upper().startswith(prefix)
        }


def _parse_ids(raw: str) -> list[int]:
    return [int(x) for x in re.findall(r"\d+", raw)] if raw.strip() else []


def _load_timezone(tz_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        sys.exit(
            "ERROR: APP_TIMEZONE is invalid or timezone data is unavailable. "
            f"Value: '{tz_name}'. "
            "Install dependencies with setup.bat (or `pip install tzdata`) "
            "and consider using APP_TIMEZONE=UTC if needed."
        )


def load_settings() -> Settings:
    """Load and validate settings from .env file."""
    load_dotenv()

    token = os.getenv("TG_BOT_TOKEN", "").strip()
    if not token:
        sys.exit("ERROR: TG_BOT_TOKEN not found in .env")

    raw_group = os.getenv("GROUP_CHAT_ID", "").strip()
    group_id = int(raw_group) if raw_group else None

    tz_name = os.getenv("APP_TIMEZONE", "America/Sao_Paulo").strip()

    return Settings(
        bot_token=token,
        group_chat_id=group_id,
        admin_user_ids=_parse_ids(os.getenv("ADMIN_USER_IDS", "")),
        operator_user_ids=_parse_ids(os.getenv("OPERATOR_USER_IDS", "")),
        viewer_user_ids=_parse_ids(os.getenv("ALLOWED_USER_IDS", "")),
        default_role=os.getenv("DEFAULT_ROLE", "none").strip().lower(),
        log_max_bytes=int(os.getenv("LOG_MAX_BYTES", str(50 * 1024 * 1024))),
        log_file=os.getenv("LOG_FILE", "logs/fluxbuddy.log").strip(),
        timezone=_load_timezone(tz_name),
    )
