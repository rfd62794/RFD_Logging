from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rfd_logging.formatter import JsonFormatter

_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT: int = 5
_DEFAULT_LEVEL: str = "INFO"

_loggers: dict[str, logging.Logger] = {}


def get_logger(
    service: str,
    log_dir: Path | str | None = None,
) -> logging.Logger:
    """
    Return a logger for the named service, creating it on first call.

    Subsequent calls with the same service name return the existing logger
    without adding duplicate handlers.

    Args:
        service:  Service identifier string — e.g. "rfd-collectors"
        log_dir:  Directory for the rotating log file.
                  Defaults to ./logs relative to the working directory.

    Environment:
        RFD_LOG_LEVEL  Sets log level for all rfd loggers. Default: INFO.
    """
    if service in _loggers:
        return _loggers[service]

    level_name = os.environ.get("RFD_LOG_LEVEL", _DEFAULT_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(f"rfd.{service}")
    logger.setLevel(level)
    logger.propagate = False

    formatter = JsonFormatter(service=service)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    resolved_log_dir = Path(log_dir) if log_dir is not None else Path("logs")
    resolved_log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        resolved_log_dir / "service.log",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _loggers[service] = logger
    return logger
