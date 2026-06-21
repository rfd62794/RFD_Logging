from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Generator


@contextmanager
def timed_operation(
    logger: logging.Logger,
    name: str,
    extra: dict | None = None,
    log_start: bool = False,
) -> Generator[None, None, None]:
    """
    Context manager that logs the duration of an operation.

    On success: logs "{name} completed" at INFO with duration_ms.
    On exception: logs "{name} failed" at ERROR with duration_ms, then re-raises.

    Args:
        logger:     Logger instance from get_logger().
        name:       Operation name — appears in the log message.
        extra:      Additional fields to include in both completion and failure entries.
        log_start:  If True, logs "{name} started" at INFO before the block runs.
                    Default False — avoids noise for short operations.

    Usage:
        with timed_operation(logger, "port_scan", extra={"range": "8000-9000"}):
            do_scan()
        # → {"message": "port_scan completed", "extra": {"range": "8000-9000", "duration_ms": 342}}
    """
    base_extra = dict(extra) if extra else {}

    if log_start:
        logger.info(f"{name} started", extra=dict(base_extra))

    start = time.monotonic()
    try:
        yield
        duration_ms = int((time.monotonic() - start) * 1000)
        completion_extra = dict(base_extra)
        completion_extra["duration_ms"] = duration_ms
        logger.info(f"{name} completed", extra=completion_extra)
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        failure_extra = dict(base_extra)
        failure_extra["duration_ms"] = duration_ms
        failure_extra["error"] = str(exc)
        logger.error(f"{name} failed", extra=failure_extra, exc_info=exc)
        raise
