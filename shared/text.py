"""Shared text processing utilities."""


def split_html_message(text: str, limit: int = 3900) -> list[str]:
    """Split a long HTML message into chunks that fit the Telegram limit (~4096)."""
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    buf: list[str] = []
    cur = 0

    for line in text.splitlines(True):
        if cur + len(line) > limit and buf:
            parts.append("".join(buf).strip())
            buf = []
            cur = 0
        buf.append(line)
        cur += len(line)

    if buf:
        parts.append("".join(buf).strip())

    return [p for p in parts if p]
