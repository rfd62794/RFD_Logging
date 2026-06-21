import logging

import pytest

import rfd_logging.config as config_module
from rfd_logging.config import get_logger
from rfd_logging.testing import capture_logs
from rfd_logging.timing import timed_operation


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


def test_completion_logged_at_info(tmp_path):
    logger = get_logger("timing-svc-1", log_dir=tmp_path)
    with capture_logs("timing-svc-1") as logs:
        with timed_operation(logger, "my_op"):
            pass
    assert logs[0]["level"] == "INFO"
    assert "completed" in logs[0]["message"]


def test_duration_ms_present_on_success(tmp_path):
    logger = get_logger("timing-svc-2", log_dir=tmp_path)
    with capture_logs("timing-svc-2") as logs:
        with timed_operation(logger, "my_op"):
            pass
    assert "duration_ms" in logs[0]["extra"]
    assert isinstance(logs[0]["extra"]["duration_ms"], int)
    assert logs[0]["extra"]["duration_ms"] >= 0


def test_failure_logged_at_error(tmp_path):
    logger = get_logger("timing-svc-3", log_dir=tmp_path)
    with capture_logs("timing-svc-3") as logs:
        with pytest.raises(ValueError):
            with timed_operation(logger, "bad_op"):
                raise ValueError("oops")
    assert logs[0]["level"] == "ERROR"
    assert "failed" in logs[0]["message"]


def test_failure_has_duration_ms(tmp_path):
    logger = get_logger("timing-svc-4", log_dir=tmp_path)
    with capture_logs("timing-svc-4") as logs:
        with pytest.raises(ValueError):
            with timed_operation(logger, "bad_op"):
                raise ValueError("oops")
    assert "duration_ms" in logs[0]["extra"]
    assert logs[0]["extra"]["duration_ms"] >= 0


def test_exception_reraised(tmp_path):
    logger = get_logger("timing-svc-5", log_dir=tmp_path)
    with pytest.raises(RuntimeError, match="propagate me"):
        with timed_operation(logger, "reraise_op"):
            raise RuntimeError("propagate me")
