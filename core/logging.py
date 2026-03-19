"""Centralized logging with bounded file size and sensitive data redaction."""

import logging
import os
import re

_SENSITIVE_PATTERNS = [
    re.compile(r"(token|secret|password|api_key)\s*[:=]\s*\S+", re.IGNORECASE),
]


class TruncatingFileHandler(logging.FileHandler):
    """Single file handler that truncates when max size is reached."""

    def __init__(self, filename: str, max_bytes: int, **kwargs):
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        super().__init__(filename, **kwargs)
        self.max_bytes = max_bytes

    def emit(self, record):
        try:
            if (
                os.path.exists(self.baseFilename)
                and os.path.getsize(self.baseFilename) >= self.max_bytes
            ):
                with open(self.baseFilename, "w", encoding=self.encoding or "utf-8"):
                    pass
        except OSError:
            pass
        super().emit(record)


class SensitiveFilter(logging.Filter):
    """Redact known sensitive patterns from log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            try:
                record.msg = record.msg % record.args
            except (TypeError, ValueError):
                pass
            record.args = None

        msg = str(record.msg)
        for pattern in _SENSITIVE_PATTERNS:
            msg = pattern.sub("[REDACTED]", msg)
        record.msg = msg
        return True


def setup_logging(log_file: str, max_bytes: int) -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("FluxBuddy")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = TruncatingFileHandler(log_file, max_bytes=max_bytes, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.setLevel(logging.INFO)
    fh.addFilter(SensitiveFilter())

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(logging.WARNING)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False

    for noisy in ("httpx", "telegram", "telegram.ext", "asyncio", "aiohttp"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger
