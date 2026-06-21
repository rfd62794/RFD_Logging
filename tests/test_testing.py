import logging

import pytest

import rfd_logging.config as config_module
from rfd_logging.config import get_logger
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


def test_capture_logs_captures_info(tmp_path):
    svc_logger = get_logger("cap-svc-1", log_dir=tmp_path)
    with capture_logs("cap-svc-1") as logs:
        svc_logger.info("hello")
    assert logs[0]["message"] == "hello"


def test_captured_entries_are_dicts(tmp_path):
    svc_logger = get_logger("cap-svc-2", log_dir=tmp_path)
    with capture_logs("cap-svc-2") as logs:
        svc_logger.info("entry")
    assert isinstance(logs[0], dict)


def test_capture_multiple_logs(tmp_path):
    svc_logger = get_logger("cap-svc-3", log_dir=tmp_path)
    with capture_logs("cap-svc-3") as logs:
        svc_logger.info("one")
        svc_logger.info("two")
        svc_logger.warning("three")
    assert len(logs) == 3


def test_capture_respects_level(tmp_path):
    svc_logger = get_logger("cap-svc-4", log_dir=tmp_path)
    svc_logger.setLevel(logging.DEBUG)
    with capture_logs("cap-svc-4", level=logging.WARNING) as logs:
        svc_logger.debug("debug msg")
        svc_logger.info("info msg")
        svc_logger.warning("warn msg")
    assert len(logs) == 1
    assert logs[0]["level"] == "WARNING"


def test_handler_removed_after_exit(tmp_path):
    svc_logger = get_logger("cap-svc-5", log_dir=tmp_path)
    count_before = len(svc_logger.handlers)
    with capture_logs("cap-svc-5") as logs:
        svc_logger.info("msg")
    assert len(svc_logger.handlers) == count_before
