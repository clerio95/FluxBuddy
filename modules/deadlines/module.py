"""Deadlines module — neutral example of date-based reminders.

Demonstrates:
- A command (/deadlines)
- A daily scheduled alert job
- Internal event publication

Configure via .env:
    DEADLINES_FILE_PATH=path/to/deadlines.csv
    DEADLINES_DATE_COLUMN=DATE
    DEADLINES_DESCRIPTION_COLUMN=DESCRIPTION
    DEADLINES_CSV_SEPARATOR=;
    DEADLINES_CSV_ENCODING=utf-8-sig
    DEADLINES_ALERT_DAYS=30
    DEADLINES_ALERT_TIME=09:10
"""

from __future__ import annotations

import csv
import html as _html
import os
from datetime import date, datetime, timedelta
from typing import Callable

from core.contracts import FluxModule, InteractionContext, ModuleContext
from core.types import CommandSpec, JobSpec, Role


def _parse_date(s: str) -> date | None:
    s = (s or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _read_csv(
    file_path: str, sep: str = ";", encoding: str = "utf-8-sig",
) -> list[dict[str, str]]:
    if not file_path or not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding=encoding) as f:
            reader = csv.DictReader(f, delimiter=sep)
            return list(reader)
    except OSError:
        return []


def _resolve_file_path(raw_path: str) -> str:
    raw = (raw_path or "").strip().strip('"').strip("'")
    if not raw:
        return ""

    expanded = os.path.expandvars(os.path.expanduser(raw))
    candidates = [expanded]

    if not os.path.isabs(expanded):
        # Try relative to current working directory first.
        candidates.append(os.path.abspath(expanded))

        # If user includes project folder name in .env, avoid duplicated prefix.
        normalized = expanded.replace("\\", "/")
        parts = [p for p in normalized.split("/") if p and p != "."]
        cwd_name = os.path.basename(os.getcwd())
        if parts and parts[0].lower() == cwd_name.lower() and len(parts) > 1:
            trimmed = os.path.join(*parts[1:])
            candidates.append(os.path.abspath(trimmed))

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if os.path.exists(candidate):
            return candidate

    return os.path.abspath(expanded) if not os.path.isabs(expanded) else expanded


def _to_int(raw: str, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _filter_upcoming(
    rows: list[dict], days: int, date_column: str,
) -> list[dict]:
    today = date.today()
    limit = today + timedelta(days=days)
    result = []
    for row in rows:
        d = _parse_date(row.get(date_column, ""))
        if d and today <= d <= limit:
            result.append({**row, "_parsed_date": d})
    result.sort(key=lambda x: x["_parsed_date"])
    return result


class DeadlinesModule(FluxModule):
    def __init__(self, ctx: ModuleContext):
        self._ctx = ctx
        self._file_path_raw = ctx.config.get("file_path", "")
        self._file_path = _resolve_file_path(self._file_path_raw)
        self._date_column = ctx.config.get("date_column", "DATE")
        self._desc_column = ctx.config.get("description_column", "DESCRIPTION")
        self._csv_sep = ctx.config.get("csv_separator", ";")
        self._csv_encoding = ctx.config.get("csv_encoding", "utf-8-sig")
        self._alert_days = _to_int(ctx.config.get("alert_days", "30"), 30)
        alert_time = ctx.config.get("alert_time", "09:10")
        parts = alert_time.split(":")
        self._alert_hour = _to_int(parts[0], 9) if len(parts) >= 2 else 9
        self._alert_minute = _to_int(parts[1], 10) if len(parts) >= 2 else 10

    @property
    def name(self) -> str:
        return "deadlines"

    @property
    def commands(self) -> list[CommandSpec]:
        return [
            CommandSpec(
                "deadlines", "Show upcoming deadlines", Role.VIEWER,
                self._cmd_deadlines,
            ),
        ]

    @property
    def jobs(self) -> list[JobSpec]:
        if not self._file_path_raw or not os.path.exists(self._file_path):
            return []
        return [
            JobSpec(
                name="deadlines.daily_alert",
                handler=self._job_daily_alert,
                daily_time=(self._alert_hour, self._alert_minute),
            ),
        ]

    async def _cmd_deadlines(self, ctx: InteractionContext) -> None:
        if not self._file_path_raw:
            await ctx.reply(
                "⚠️ <b>Deadlines file not configured.</b>\n\n"
                "Set <code>DEADLINES_FILE_PATH</code> in .env"
            )
            return

        if not os.path.exists(self._file_path):
            await ctx.reply(
                "⚠️ <b>Deadlines file not found.</b>\n\n"
                f"Configured: <code>{_html.escape(self._file_path_raw)}</code>\n"
                f"Resolved: <code>{_html.escape(self._file_path)}</code>\n\n"
                "Tip: use a path relative to project root, e.g. "
                "<code>teste_deadlines/deadlines.csv</code>"
            )
            return

        rows = _read_csv(self._file_path, self._csv_sep, self._csv_encoding)
        upcoming = _filter_upcoming(rows, self._alert_days, self._date_column)

        if not upcoming:
            await ctx.reply(
                f"✅ No deadlines in the next {self._alert_days} days."
            )
            return

        text = f"📅 <b>UPCOMING DEADLINES</b> (next {self._alert_days} days)\n\n"
        for item in upcoming:
            d = item["_parsed_date"].strftime("%d/%m/%Y")
            desc = _html.escape(item.get(self._desc_column, "—"))
            remaining = (item["_parsed_date"] - date.today()).days
            emoji = "🔴" if remaining <= 7 else "🟡" if remaining <= 14 else "🟢"
            text += f"{emoji} <b>{d}</b> — {desc} ({remaining}d)\n"

        await ctx.reply(text.strip())

    async def _job_daily_alert(self, send_to_group: Callable) -> None:
        rows = _read_csv(self._file_path, self._csv_sep, self._csv_encoding)
        upcoming = _filter_upcoming(rows, self._alert_days, self._date_column)

        if not upcoming:
            return

        text = f"⏰ <b>DEADLINE ALERT</b> (next {self._alert_days} days)\n\n"
        for item in upcoming:
            d = item["_parsed_date"].strftime("%d/%m/%Y")
            desc = _html.escape(item.get(self._desc_column, "—"))
            remaining = (item["_parsed_date"] - date.today()).days
            emoji = "🔴" if remaining <= 7 else "🟡" if remaining <= 14 else "🟢"
            text += f"{emoji} <b>{d}</b> — {desc} ({remaining}d)\n"

        await send_to_group(text.strip())

        await self._ctx.event_bus.publish("deadlines.alert_sent", {
            "count": len(upcoming),
        })


def create_module(ctx: ModuleContext) -> FluxModule:
    return DeadlinesModule(ctx)
