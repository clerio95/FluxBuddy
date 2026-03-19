"""Occurrences module — neutral example of file-based alerting.

Demonstrates:
- A command (/occurrences)
- A recurring scan job
- Internal event publication on new entries

Configure via .env:
    OCCURRENCES_FILE_PATH=path/to/occurrences.txt
    OCCURRENCES_POLL_INTERVAL=120
"""

from __future__ import annotations

import hashlib
import html as _html
import os
import re
from typing import Callable

from core.contracts import FluxModule, InteractionContext, ModuleContext
from core.types import CommandSpec, JobSpec, Role

_RE_ENTRY_START = re.compile(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+-\s+.*")
_LAST_HASH_FILE = "data/occurrences_last_hash.txt"


def _hash_text(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8", errors="replace")).hexdigest()


def _read_entries(file_path: str) -> list[str]:
    if not file_path or not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return []

    entries: list[str] = []
    block: list[str] = []
    for ln in lines:
        ln = ln.rstrip()
        if _RE_ENTRY_START.match(ln):
            if block:
                entries.append("\n".join(block))
            block = [ln]
        elif block:
            block.append(ln)
    if block:
        entries.append("\n".join(block))
    return entries


class OccurrencesModule(FluxModule):
    def __init__(self, ctx: ModuleContext):
        self._ctx = ctx
        self._file_path = ctx.config.get("file_path", "")
        poll_raw = ctx.config.get("poll_interval", "120")
        self._poll_interval = int(poll_raw) if poll_raw.isdigit() else 120

    @property
    def name(self) -> str:
        return "occurrences"

    @property
    def commands(self) -> list[CommandSpec]:
        return [
            CommandSpec(
                "occurrences", "Show recent entries", Role.VIEWER,
                self._cmd_occurrences,
            ),
        ]

    @property
    def jobs(self) -> list[JobSpec]:
        if not self._file_path:
            return []
        return [
            JobSpec(
                name="occurrences.scan",
                handler=self._job_scan,
                interval_seconds=self._poll_interval,
            ),
        ]

    async def _cmd_occurrences(self, ctx: InteractionContext) -> None:
        if not self._file_path:
            await ctx.reply(
                "⚠️ <b>Occurrences file not configured.</b>\n\n"
                "Set <code>OCCURRENCES_FILE_PATH</code> in .env"
            )
            return

        entries = _read_entries(self._file_path)
        last_10 = entries[-10:]

        if not last_10:
            await ctx.reply("📋 No occurrences found.")
            return

        text = "<b>📋 RECENT OCCURRENCES</b>\n\n"
        for i, entry in enumerate(reversed(last_10), 1):
            lines = entry.split("\n", 1)
            header = _html.escape(lines[0].strip())
            body = _html.escape(lines[1].strip()) if len(lines) > 1 else ""
            text += f"<b>{i:02d}.</b> <i>{header}</i>\n"
            if body:
                text += f"{body}\n"
            text += "\n"

        await ctx.reply(text.strip())

    async def _job_scan(self, send_to_group: Callable) -> None:
        entries = _read_entries(self._file_path)
        if not entries:
            return

        latest = entries[-1].strip()
        latest_hash = _hash_text(latest)

        saved_hash = ""
        if os.path.exists(_LAST_HASH_FILE):
            try:
                with open(_LAST_HASH_FILE, "r", encoding="utf-8") as f:
                    saved_hash = f.read().strip()
            except OSError:
                pass

        if saved_hash == latest_hash:
            return

        lines = latest.split("\n", 1)
        header = _html.escape(lines[0].strip())
        body = _html.escape(lines[1].strip()) if len(lines) > 1 else ""

        text = f"🚨 <b>NEW OCCURRENCE</b>\n\n<b>{header}</b>\n"
        if body:
            text += f"{body}\n"

        await send_to_group(text.strip())

        os.makedirs(os.path.dirname(_LAST_HASH_FILE), exist_ok=True)
        with open(_LAST_HASH_FILE, "w", encoding="utf-8") as f:
            f.write(latest_hash)

        await self._ctx.event_bus.publish("occurrences.new_entry", {
            "header": lines[0].strip(),
        })


def create_module(ctx: ModuleContext) -> FluxModule:
    return OccurrencesModule(ctx)
