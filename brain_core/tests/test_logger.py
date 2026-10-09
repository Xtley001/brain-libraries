"""Unit tests — brain_core.logger"""
import logging
from brain_core.logger import get_logger


def test_get_logger_returns_logger():
    log = get_logger("test.brain_core.logger")
    assert isinstance(log, logging.Logger)
    assert log.name == "test.brain_core.logger"


def test_get_logger_explicit_level():
    log = get_logger("test.brain_core.debug", level=logging.DEBUG)
    assert log.level == logging.DEBUG
