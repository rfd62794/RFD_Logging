from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from rfd_logging.context import get_request_id

_STANDARD_ATTRS: frozenset[str] = frozenset({
    "args", "created", "exc_info", "exc_text", "filename", "funcName",
    "levelname", "levelno", "lineno", "message", "module", "msecs",
    "msg", "name", "pathname", "process", "processName", "relativeCreated",
    "stack_info", "taskName", "thread", "threadName", "asctime",
})


def _make_json_safe(extra: dict) -> dict:
    """Replace any non-JSON-serialisable values in extra with their repr()."""
    safe: dict = {}
    for k, v in extra.items():
        try:
            json.dumps(v)
            safe[k] = v
        except (TypeError, ValueError):
            safe[k] = repr(v)
    return safe


class JsonFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON matching the RFD logging standard.

    Output fields (always present):
        timestamp   ISO 8601 UTC with milliseconds — "2026-06-21T20:38:33.092Z"
        level       DEBUG | INFO | WARNING | ERROR | CRITICAL
        service     Name passed at formatter construction
        message     Rendered log message
        extra       Dict of caller-supplied extra fields (empty dict if none)
        request_id  Reserved for Gateway tracing (null if not set)

    Output fields (conditional):
        error       String error description when passed as extra field
        traceback   Exception traceback string when exc_info is set
    """

    def __init__(self, service: str = "unknown") -> None:
        super().__init__()
        self._service = service

    def format(self, record: logging.LogRecord) -> str:
        try:
            extra: dict = {
                k: v
                for k, v in record.__dict__.items()
                if k not in _STANDARD_ATTRS and not k.startswith("_")
            }

            request_id = extra.pop("request_id", None)
            if request_id is None:
                request_id = get_request_id()
            error = extra.pop("error", None)

            ms = int(record.msecs)
            ts = datetime.fromtimestamp(record.created, tz=timezone.utc)
            timestamp = ts.strftime(f"%Y-%m-%dT%H:%M:%S.{ms:03d}Z")

            entry: dict = {
                "timestamp": timestamp,
                "level": record.levelname,
                "service": self._service,
                "message": record.getMessage(),
                "extra": extra,
                "request_id": request_id,
            }

            if error is not None:
                entry["error"] = str(error)

            if record.exc_info:
                entry["traceback"] = self.formatException(record.exc_info)

            try:
                return json.dumps(entry, ensure_ascii=False)
            except (TypeError, ValueError):
                entry["extra"] = _make_json_safe(extra)
                try:
                    return json.dumps(entry, ensure_ascii=False)
                except (TypeError, ValueError):
                    return json.dumps({
                        "timestamp": timestamp,
                        "level": record.levelname,
                        "service": self._service,
                        "message": repr(record.getMessage()),
                        "extra": {},
                        "request_id": request_id,
                        "error": "JsonFormatter: serialisation error",
                    }, ensure_ascii=False)
        except Exception as exc:  # absolute last resort — format() must never raise
            return json.dumps({
                "timestamp": "",
                "level": "ERROR",
                "service": self._service,
                "message": f"JsonFormatter internal error: {exc!r}",
                "extra": {},
                "request_id": None,
            }, ensure_ascii=False)
