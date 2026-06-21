import logging

import pytest

import rfd_logging.config as config_module
from rfd_logging.config import get_logger
from rfd_logging.helpers import log_exception
from rfd_logging.testing import capture_logs


@pytest.fixture(autouse=True)
def clear_loggers():
    """Clear logger cache and close all file handlers before and after each test."""
    def _flush_and_clear():
        for logger in list(config_module._loggers.values()):
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        config_module._loggers.clear()

    _flush_and_clear()
    yield
    _flush_and_clear()


def test_logs_at_error_level(tmp_path):
    logger = get_logger("hlp-svc-1", log_dir=tmp_path)
    exc = ValueError("boom")
    with capture_logs("hlp-svc-1") as logs:
        log_exception(logger, exc)
    assert logs[0]["level"] == "ERROR"


def test_error_field_contains_exception_str(tmp_path):
    logger = get_logger("hlp-svc-2", log_dir=tmp_path)
    exc = ValueError("boom")
    with capture_logs("hlp-svc-2") as logs:
        log_exception(logger, exc)
    assert logs[0]["error"] == "boom"


def test_traceback_field_present(tmp_path):
    logger = get_logger("hlp-svc-3", log_dir=tmp_path)
    try:
        raise ValueError("raised error")
    except ValueError as e:
        exc = e
    with capture_logs("hlp-svc-3") as logs:
        log_exception(logger, exc, "caught it")
    assert "traceback" in logs[0]


def test_does_not_mutate_caller_extra(tmp_path):
    logger = get_logger("hlp-svc-4", log_dir=tmp_path)
    caller_extra = {"k": "v"}
    exc = ValueError("boom")
    with capture_logs("hlp-svc-4") as logs:
        log_exception(logger, exc, extra=caller_extra)
    assert caller_extra == {"k": "v"}
