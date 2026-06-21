import json
import logging

from rfd_logging.formatter import JsonFormatter
from rfd_logging.redaction import REDACT_FIELDS, redact


def test_redacts_known_field():
    result = redact({"password": "abc"})
    assert result["password"] == "[REDACTED]"


def test_case_insensitive():
    result = redact({"PASSWORD": "abc"})
    assert result["PASSWORD"] == "[REDACTED]"


def test_non_sensitive_unchanged():
    result = redact({"service": "rfd-collectors"})
    assert result["service"] == "rfd-collectors"


def test_does_not_mutate_input():
    original = {"password": "abc", "service": "rfd"}
    before = dict(original)
    redact(original)
    assert original == before


def test_custom_fields_override():
    result = redact(
        {"myfield": "sensitive", "password": "should_stay"},
        fields=frozenset({"myfield"}),
    )
    assert result["myfield"] == "[REDACTED]"
    assert result["password"] == "should_stay"


def test_auto_redaction_in_formatter():
    formatter = JsonFormatter(service="redact-svc")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="connecting",
        args=(),
        exc_info=None,
    )
    record.api_key = "secret123"
    record.host = "localhost"
    parsed = json.loads(formatter.format(record))
    assert parsed["extra"]["api_key"] == "[REDACTED]"
    assert parsed["extra"]["host"] == "localhost"
