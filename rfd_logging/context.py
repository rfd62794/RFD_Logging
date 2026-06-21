from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Generator

_request_id: ContextVar[str | None] = ContextVar("rfd_request_id", default=None)


def get_request_id() -> str | None:
    """Return the current request ID from context, or None if not set."""
    return _request_id.get()


@contextmanager
def request_context(request_id: str) -> Generator[None, None, None]:
    """
    Context manager that sets a request ID for all logs emitted within the block.

    The request_id flows into log output automatically — no need to pass it
    to every logger.info() call.

    Usage:
        with request_context("abc-123"):
            logger.info("fetching repos")   # → request_id: "abc-123"
            logger.info("repos fetched")    # → request_id: "abc-123"
    """
    token = _request_id.set(request_id)
    try:
        yield
    finally:
        _request_id.reset(token)
