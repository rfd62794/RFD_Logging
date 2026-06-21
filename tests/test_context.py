import json
import logging

from rfd_logging.context import get_request_id, request_context
from rfd_logging.formatter import JsonFormatter


def test_request_id_set_within_context():
    with request_context("x"):
        assert get_request_id() == "x"


def test_request_id_none_outside_context():
    assert get_request_id() is None


def test_context_restores_after_exit():
    with request_context("temp"):
        pass
    assert get_request_id() is None


def test_nested_contexts_restore_correctly():
    with request_context("outer"):
        assert get_request_id() == "outer"
        with request_context("inner"):
            assert get_request_id() == "inner"
        assert get_request_id() == "outer"
    assert get_request_id() is None


def test_request_id_appears_in_log_output():
    formatter = JsonFormatter(service="ctx-svc")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test msg",
        args=(),
        exc_info=None,
    )
    with request_context("req-1"):
        result = formatter.format(record)
    parsed = json.loads(result)
    assert parsed["request_id"] == "req-1"
