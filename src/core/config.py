"""Application environment configuration provider

Copy `.env.example` to `.env` for pure usa
or to `.env.docker` for docker-based use.
Or setup environment variables use system methods.
"""
import logging
from dataclasses import dataclass
from functools import lru_cache

from environs import Env

from src.core.logging import LoggingLevelType


@dataclass
class APIConfig:
    log_level: int | LoggingLevelType = logging.INFO
    rabbitmq_uri: str = "amqp://guest:guest@127.0.0.1/"
    rabbitmq_exchange_rate_channel: str = "exchange-rate"
    enable_metrics: bool = True


@dataclass
class ExchangeMonitorConfig:
    log_level: int | LoggingLevelType = logging.INFO
    rabbitmq_uri: str = "amqp://guest:guest@127.0.0.1/"
    rabbitmq_exchange_rate_channel: str = "exchange-rate"
    binance_api_key: str | None = None
    binance_api_secret: str | None = None


@lru_cache()
def get_api_config() -> APIConfig:
    env = Env()
    env.read_env()

    return APIConfig(
        log_level=env.log_level("LOG_LEVEL", APIConfig.log_level),
        rabbitmq_uri=env.str("RABBITMQ_URI", APIConfig.rabbitmq_uri),
        rabbitmq_exchange_rate_channel=env.str(
            "RABBITMQ_EXCHANGE_RATE_CHANNEL",
            APIConfig.rabbitmq_exchange_rate_channel,
        ),
        enable_metrics=env.bool("ENABLE_METRICS", APIConfig.enable_metrics),
    )


@lru_cache()
def get_exchange_monitor_config() -> ExchangeMonitorConfig:
    env = Env()
    env.read_env()

    return ExchangeMonitorConfig(
        log_level=env.log_level("LOG_LEVEL", ExchangeMonitorConfig.log_level),
        rabbitmq_uri=env.str("RABBITMQ_URI", ExchangeMonitorConfig.rabbitmq_uri),
        rabbitmq_exchange_rate_channel=env.str(
            "RABBITMQ_EXCHANGE_RATE_CHANNEL",
            ExchangeMonitorConfig.rabbitmq_exchange_rate_channel,
        ),
        binance_api_key=env.str("BINANCE_API_KEY"),
        binance_api_secret=env.str("BINANCE_API_SECRET"),
    )


__all__ = [
    "get_api_config",
    "APIConfig",
    "get_exchange_monitor_config",
    "ExchangeMonitorConfig",
]
