# rfd-logging

Standardised JSON logging for RFD services. One line per entry, machine-parseable, zero dependencies.

---

## Installation

**From PyPI:**
```bash
pip install rfd-logging
```

**Editable local install (for RFD services):**
```bash
uv add --editable C:\Github\RFD_Logging
```

---

## Usage

```python
from rfd_logging import get_logger

logger = get_logger("rfd-collectors", log_dir="logs")

# Basic info
logger.info("Service started")

# With extra fields
logger.info("Request received", extra={"endpoint": "/api/data", "request_id": "req-abc123"})

# Error with description
logger.error("Database unreachable", extra={"error": "Connection refused", "host": "db.local"})

# Exception with traceback
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Unhandled error during processing")
```

### Sample JSON output

```json
{"timestamp": "2026-06-21T20:38:33.092Z", "level": "INFO", "service": "rfd-collectors", "message": "Request received", "extra": {"endpoint": "/api/data"}, "request_id": "req-abc123"}
{"timestamp": "2026-06-21T20:38:33.105Z", "level": "ERROR", "service": "rfd-collectors", "message": "Database unreachable", "extra": {"host": "db.local"}, "request_id": null, "error": "Connection refused"}
{"timestamp": "2026-06-21T20:38:33.110Z", "level": "ERROR", "service": "rfd-collectors", "message": "Unhandled error during processing", "extra": {}, "request_id": null, "traceback": "Traceback (most recent call last):\n  ..."}
```

---

## Output fields

| Field | Always present | Description |
|---|---|---|
| `timestamp` | ✓ | ISO 8601 UTC with milliseconds — `2026-06-21T20:38:33.092Z` |
| `level` | ✓ | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` |
| `service` | ✓ | Service name passed to `get_logger` |
| `message` | ✓ | Rendered log message |
| `extra` | ✓ | Dict of caller-supplied extra fields (empty dict if none) |
| `request_id` | ✓ | Gateway trace ID — `null` if not set |
| `error` | Conditional | String error description when `extra={"error": ...}` is passed |
| `traceback` | Conditional | Exception traceback when `exc_info` is set (e.g. via `logger.exception`) |

---

## Configuration

### Log level

Set via environment variable before starting the service:

```bash
set RFD_LOG_LEVEL=DEBUG   # Windows
export RFD_LOG_LEVEL=DEBUG  # Linux/macOS
```

Default: `INFO`. Valid values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

The variable is read at the time `get_logger` is first called for a given service — not at import time.

---

## Log file location and rotation

`get_logger(service, log_dir)` writes to `{log_dir}/service.log`.

- **Default `log_dir`:** `./logs` relative to the working directory
- **Rotation:** 10 MB per file, 5 backups kept (`service.log`, `service.log.1` … `service.log.5`)
- **Encoding:** UTF-8
- **Also emits to stdout** for NSSM `AppStdout` capture

The `log_dir` is created automatically (including parents) if it does not exist.

---

## Idempotent logger creation

`get_logger` is safe to call multiple times with the same service name — subsequent calls return the cached logger without adding duplicate handlers:

```python
logger_a = get_logger("my-service", log_dir="logs")
logger_b = get_logger("my-service", log_dir="logs")
assert logger_a is logger_b  # True
```

---

## Zero dependencies

`rfd-logging` uses only the Python standard library: `logging`, `json`, `datetime`, `pathlib`, `os`. No third-party packages are installed.

---

## Requirements

- Python ≥ 3.11
