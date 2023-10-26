"""FastAPI depends for exchange rate"""
from fastapi import Depends

from src.adapters.queue.abc import EventBus
from src.adapters.queue.third_party.rabbitmq.queue import get_rabbitmq
from src.core import APIConfig, get_api_config
from src.modules.api.exchange_rate_store import ExchangeRateStore
from src.modules.api.exchange_rate_store import (
    get_exchange_rate_store as _get_exchange_rate_store,
)


def get_exchange_update_queue(
    config: APIConfig = Depends(get_api_config),
) -> EventBus:
    return get_rabbitmq(
        config.rabbitmq_exchange_rate_channel,
        config.rabbitmq_uri,
    )


def get_exchange_rate_store(
    exchange_update_queue: EventBus = Depends(get_exchange_update_queue),
    config: APIConfig = Depends(get_api_config),
) -> ExchangeRateStore:
    return _get_exchange_rate_store(
        exchange_update_queue,
        enable_metrics=config.enable_metrics,
    )


__all__ = ["get_exchange_rate_store"]
