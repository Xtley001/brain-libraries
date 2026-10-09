"""
Consistent structured logger factory for all Brain libraries.

Usage
-----
    from brain_core.logger import get_logger
    log = get_logger("brain_options.run")
    log.info("Pipeline started")

Format:  %(asctime)s | %(levelname)-8s | %(name)s | %(message)s
Level:   Read from LOG_LEVEL env var (default: INFO).
         Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_root_configured = False


def _configure_root() -> None:
    global _root_configured
    if _root_configured:
        return
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(_FORMATTER)
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(level)
    _root_configured = True


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Return a logger named *name* with the Brain standard formatter applied.

    Parameters
    ----------
    name  : Logger name, e.g. "brain_options.run" or __name__.
    level : Optional explicit level override (logging.DEBUG etc.).
            Defaults to the root level set by LOG_LEVEL env var.
    """
    _configure_root()
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger
