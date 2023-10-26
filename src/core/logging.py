"""Application logging

Typical usage example:

    _logger: Logger = get_logger("module-name")
"""
from logging import Logger, getLogger, basicConfig
from typing import Literal

_app_logger = getLogger("app")

LoggingLevelType = Literal[
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
]


def get_logger(name: str | None = None) -> Logger:
    """Returns logger

    :param name: (Optional) name of logger
    :return: if name is None return global logger else return module logger
    """
    if name:
        return _app_logger.getChild(name)
    return _app_logger


def configure_logging(level: int | LoggingLevelType = "INFO"):
    basicConfig(level=level)
    getLogger("aio_pika.queue").setLevel("INFO")
    getLogger("aio_pika.connection").setLevel("INFO")
    getLogger("aio_pika.exchange").setLevel("INFO")
    getLogger("aiormq.connection").setLevel("INFO")
    getLogger("websockets.client").setLevel("INFO")
    getLogger("binance.streams").setLevel("CRITICAL")


__all__ = [
    "get_logger",
    "configure_logging",
    "LoggingLevelType",
]
