from __future__ import annotations

import logging


def log_exception(
    logger: logging.Logger,
    exc: Exception,
    message: str = "An error occurred",
    extra: dict | None = None,
) -> None:
    """
    Log an exception with standardised RFD field population.

    Populates:
        message   — the message parameter
        error     — str(exc)
        traceback — exception traceback via exc_info

    Usage:
        try:
            do_something()
        except Exception as e:
            log_exception(logger, e, "Failed to fetch repos")
    """
    log_extra = dict(extra) if extra else {}
    log_extra["error"] = str(exc)
    logger.error(message, extra=log_extra, exc_info=exc)
