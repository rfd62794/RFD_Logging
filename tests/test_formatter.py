import json
import logging
import sys

from rfd_logging.formatter import JsonFormatter


def _make_record(
    msg: str = "hello",
    level: int = logging.INFO,
    exc_info=None,
    **extra_attrs,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test",
        level=level,
        pathname="test.py",
        lineno=1,
        msg=msg,
        args=(),
        exc_info=exc_info,
    )
    for k, v in extra_attrs.items():
        setattr(record, k, v)
    return record


def test_output_is_valid_json():
    formatter = JsonFormatter(service="test-svc")
    record = _make_record()
    result = formatter.format(record)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_mandatory_fields_present():
    formatter = JsonFormatter(service="test-svc")
    record = _make_record()
    parsed = json.loads(formatter.format(record))
    for field in ("timestamp", "level", "service", "message", "extra", "request_id"):
        assert field in parsed, f"Missing mandatory field: {field}"


def test_extra_fields_in_extra_dict():
    formatter = JsonFormatter(service="test-svc")
    record = _make_record(key="val")
    parsed = json.loads(formatter.format(record))
    assert parsed["extra"].get("key") == "val"


def test_request_id_passed_through():
    formatter = JsonFormatter(service="test-svc")
    record = _make_record(request_id="abc")
    parsed = json.loads(formatter.format(record))
    assert parsed["request_id"] == "abc"
    assert "request_id" not in parsed.get("extra", {})


def test_error_field_included():
    formatter = JsonFormatter(service="test-svc")
    record = _make_record(error="boom")
    parsed = json.loads(formatter.format(record))
    assert parsed["error"] == "boom"
    assert "error" not in parsed.get("extra", {})


def test_traceback_on_exc_info():
    formatter = JsonFormatter(service="test-svc")
    try:
        raise ValueError("test error")
    except ValueError:
        exc_info = sys.exc_info()
    record = _make_record(exc_info=exc_info)
    parsed = json.loads(formatter.format(record))
    assert "traceback" in parsed
    assert "ValueError" in parsed["traceback"]
