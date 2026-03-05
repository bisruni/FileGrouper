"""Central logging configuration and helpers for ArchiFlow."""

from __future__ import annotations

import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock
from typing import Any

from .constants import LOGS_DIRNAME, app_state_dir

LOGGER_NAME = "archiflow"
DEFAULT_LOG_FILE_NAME = "archiflow.log"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 5

_CONFIG_LOCK = Lock()
_CONFIGURED = False
_ACTIVE_LOG_FILE: Path | None = None


class KeyValueFormatter(logging.Formatter):
    """Serialize log records as compact key=value structured lines."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record into deterministic key=value structure."""
        timestamp = self.formatTime(record, "%Y-%m-%dT%H:%M:%S")
        message = record.getMessage().replace("\n", "\\n")
        parts = [
            f"ts={timestamp}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"module={record.module}",
            f"line={record.lineno}",
            f"msg={message!r}",
        ]
        transaction_id = getattr(record, "transaction_id", None)
        if transaction_id:
            parts.append(f"transaction_id={transaction_id}")
        return " ".join(parts)


def _parse_level(value: str | None) -> int:
    """Resolve textual log level to numeric logging level."""
    if not value:
        return logging.INFO
    resolved = logging.getLevelName(value.upper())
    return resolved if isinstance(resolved, int) else logging.INFO


def _resolve_log_dir(log_dir: Path | None) -> Path:
    """Resolve effective log directory using env override and defaults."""
    env_dir = os.environ.get("ARCHIFLOW_LOG_DIR", "").strip()
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    if log_dir is not None:
        return log_dir.expanduser().resolve()
    return (app_state_dir(Path.cwd()) / LOGS_DIRNAME).resolve()


def configure_logging(
    *,
    log_dir: Path | None = None,
    level: str | None = None,
    force: bool = False,
) -> Path:
    """Configure root ArchiFlow logger and return active log file path."""
    global _CONFIGURED, _ACTIVE_LOG_FILE

    with _CONFIG_LOCK:
        if _CONFIGURED and not force and _ACTIVE_LOG_FILE is not None:
            return _ACTIVE_LOG_FILE

        configured_level = _parse_level(level or os.environ.get("ARCHIFLOW_LOG_LEVEL"))
        console_level = _parse_level(os.environ.get("ARCHIFLOW_CONSOLE_LOG_LEVEL", "WARNING"))
        resolved_log_dir = _resolve_log_dir(log_dir)
        try:
            resolved_log_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Last-resort fallback: temp directory should always be writable.
            resolved_log_dir = (Path(tempfile.gettempdir()) / "archiflow-logs").resolve()
            resolved_log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = resolved_log_dir / DEFAULT_LOG_FILE_NAME

        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(configured_level)
        logger.handlers.clear()
        logger.propagate = False

        formatter = KeyValueFormatter()

        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=DEFAULT_MAX_BYTES,
            backupCount=DEFAULT_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(configured_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        _ACTIVE_LOG_FILE = log_file_path
        _CONFIGURED = True
        logger.info("Logging configured", extra={"transaction_id": ""})
        return log_file_path


def get_logger(name: str | None = None) -> logging.Logger:
    """Return configured project logger or a named child logger."""
    if not _CONFIGURED:
        configure_logging()
    if not name:
        return logging.getLogger(LOGGER_NAME)
    if name.startswith(LOGGER_NAME):
        return logging.getLogger(name)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def get_active_log_file() -> Path | None:
    """Return currently active rotating log file path if configured."""
    return _ACTIVE_LOG_FILE


def log_exception(logger: logging.Logger, message: str, **extra: Any) -> None:
    """Convenience helper to log full exception traceback with metadata."""
    logger.exception(message, extra=extra)
