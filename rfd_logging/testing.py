from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from typing import Generator

from rfd_logging.formatter import JsonFormatter


@contextmanager
def capture_logs(
    service: str,
    level: int = logging.DEBUG,
) -> Generator[list[dict], None, None]:
    """
    Context manager that captures log output for a named service as parsed dicts.

    Adds a temporary handler to the named logger for the duration of the block.
    Handler is removed on exit regardless of exceptions.

    Usage:
        with capture_logs("my-service") as logs:
            logger = get_logger("my-service")
            logger.info("hello")

        assert logs[0]["message"] == "hello"
        assert logs[0]["level"] == "INFO"
    """
    captured: list[dict] = []

    class _CapturingHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                formatter = JsonFormatter(service=service)
                line = formatter.format(record)
                captured.append(json.loads(line))
            except Exception:
                pass

    logger = logging.getLogger(f"rfd.{service}")
    handler = _CapturingHandler(level=level)
    logger.addHandler(handler)

    try:
        yield captured
    finally:
        logger.removeHandler(handler)
