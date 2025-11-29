"""Console helpers for colorful logging and progress output."""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

RESET = "\033[0m"
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
}
LEVEL_COLORS = {
    logging.DEBUG: "blue",
    logging.INFO: "green",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "red",
}


def supports_color(stream: Optional[object] = None) -> bool:
    stream = stream or sys.stdout
    return hasattr(stream, "isatty") and stream.isatty() and os.getenv("TERM") != "dumb"


def colorize(text: str, color: str | None = None, *, bold: bool = False) -> str:
    if not supports_color():
        return text
    prefix = ""
    if bold:
        prefix += COLORS["bold"]
    if color and color in COLORS:
        prefix += COLORS[color]
    if not prefix:
        return text
    return f"{prefix}{text}{RESET}"


class ColorFormatter(logging.Formatter):
    """Logging formatter that colors the entire log line by level."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        color = LEVEL_COLORS.get(record.levelno)
        if not color or not supports_color():
            return message
        return f"{COLORS[color]}{message}{RESET}"


def configure_logging(verbose: bool) -> None:
    """Configure root logger with optional colorized output."""
    level = logging.INFO if verbose else logging.WARNING
    handler = logging.StreamHandler()
    formatter = ColorFormatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

