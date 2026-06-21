import logging
from logging.handlers import RotatingFileHandler

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


def test_returns_logger_instance(tmp_path):
    logger = get_logger("cfg-svc-1", log_dir=tmp_path)
    assert isinstance(logger, logging.Logger)


def test_idempotent_no_duplicate_handlers(tmp_path):
    logger1 = get_logger("cfg-svc-2", log_dir=tmp_path)
    handler_count = len(logger1.handlers)
    logger2 = get_logger("cfg-svc-2", log_dir=tmp_path)
    assert logger1 is logger2
    assert len(logger2.handlers) == handler_count


def test_default_level_is_info(tmp_path, monkeypatch):
    monkeypatch.delenv("RFD_LOG_LEVEL", raising=False)
    logger = get_logger("cfg-svc-3", log_dir=tmp_path)
    assert logger.level == logging.INFO


def test_env_level_override(tmp_path, monkeypatch):
    monkeypatch.setenv("RFD_LOG_LEVEL", "DEBUG")
    logger = get_logger("cfg-svc-4", log_dir=tmp_path)
    assert logger.level == logging.DEBUG


def test_creates_log_directory(tmp_path):
    new_dir = tmp_path / "new_subdir"
    assert not new_dir.exists()
    get_logger("cfg-svc-5", log_dir=new_dir)
    assert new_dir.exists()


def test_file_handler_present(tmp_path):
    logger = get_logger("cfg-svc-6", log_dir=tmp_path)
    handler_types = [type(h) for h in logger.handlers]
    assert RotatingFileHandler in handler_types


def test_console_handler_present(tmp_path):
    logger = get_logger("cfg-svc-7", log_dir=tmp_path)
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types
