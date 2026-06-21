import json
import logging

import pytest

import rfd_logging.config as config_module
from rfd_logging.config import get_logger


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


def test_info_log_written_to_file(tmp_path):
    logger = get_logger("integ-svc-1", log_dir=tmp_path)
    logger.info("hello")
    for h in logger.handlers:
        h.flush()

    log_file = tmp_path / "service.log"
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    parsed = json.loads(lines[0])
    assert parsed["message"] == "hello"
    for field in ("timestamp", "level", "service", "message", "extra", "request_id"):
        assert field in parsed, f"Missing mandatory field: {field}"


def test_error_with_extra_written(tmp_path):
    logger = get_logger("integ-svc-2", log_dir=tmp_path)
    logger.error("err", extra={"error": "e"})
    for h in logger.handlers:
        h.flush()

    log_file = tmp_path / "service.log"
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    parsed = json.loads(lines[0])
    assert parsed["error"] == "e"


def test_service_name_in_output(tmp_path):
    logger = get_logger("my-special-service", log_dir=tmp_path)
    logger.info("line1")
    logger.warning("line2")
    for h in logger.handlers:
        h.flush()

    log_file = tmp_path / "service.log"
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 2
    for line in lines:
        parsed = json.loads(line)
        assert parsed["service"] == "my-special-service"
