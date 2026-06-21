import logging

import pytest

import rfd_logging.config as config_module
from rfd_logging.config import _get_level, get_logger


@pytest.fixture(autouse=True)
def clear_loggers(monkeypatch):
    """Clear logger cache and remove all level-related env vars before each test."""
    def _flush_and_clear():
        for logger in list(config_module._loggers.values()):
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        config_module._loggers.clear()

    _flush_and_clear()
    monkeypatch.delenv("RFD_LOG_LEVEL", raising=False)
    monkeypatch.delenv("RFD_LOG_LEVEL_ANY_SERVICE", raising=False)
    monkeypatch.delenv("RFD_LOG_LEVEL_MY_SERVICE", raising=False)
    monkeypatch.delenv("RFD_LOG_LEVEL_RFD_COLLECTORS", raising=False)
    monkeypatch.delenv("RFD_LOG_LEVEL_RFD_TEST", raising=False)
    yield
    _flush_and_clear()


def test_default_level_is_info(monkeypatch):
    monkeypatch.delenv("RFD_LOG_LEVEL", raising=False)
    assert _get_level("any-service") == logging.INFO


def test_global_override(monkeypatch):
    monkeypatch.setenv("RFD_LOG_LEVEL", "DEBUG")
    assert _get_level("any-service") == logging.DEBUG


def test_service_specific_override(monkeypatch):
    monkeypatch.setenv("RFD_LOG_LEVEL_MY_SERVICE", "WARNING")
    assert _get_level("my-service") == logging.WARNING


def test_service_override_wins_over_global(monkeypatch):
    monkeypatch.setenv("RFD_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("RFD_LOG_LEVEL_MY_SERVICE", "DEBUG")
    assert _get_level("my-service") == logging.DEBUG


def test_hyphen_to_underscore_normalisation(monkeypatch):
    monkeypatch.setenv("RFD_LOG_LEVEL_RFD_COLLECTORS", "DEBUG")
    assert _get_level("rfd-collectors") == logging.DEBUG
