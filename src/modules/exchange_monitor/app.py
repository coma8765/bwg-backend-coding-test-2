"""Exchange rate monitor

Algorithm:
    * get data from binance, coingecko, etc...
    * send their to defined channel using event bus
"""
import asyncio

from src.adapters.exchange_observer.abc import ExchangeObserver
from src.adapters.exchange_observer.controller import ExchangeUpdateController
from src.adapters.exchange_observer.models import ExchangeRate
from src.adapters.exchange_observer.third_party.binance import (
    BinanceConfig,
    BinanceObserver,
)
from src.adapters.exchange_observer.third_party.coingecko.config import (
    CoingeckoConfig,
)
from src.adapters.exchange_observer.third_party.coingecko.exchange_observer import (
    CoingeckoObserver,
)
from src.adapters.queue.abc import EventBus
from src.adapters.queue.third_party.rabbitmq.queue import get_rabbitmq
from src.core import configure_logging
from src.core.config import get_exchange_monitor_config


class ExchangeUpdateMonitor(ExchangeUpdateController):
    __slots__ = ("_event_bus",)
    _event_bus: EventBus

    def __init__(self, *observables: ExchangeObserver, event_bus):
        super().__init__(*observables)
        self._event_bus = event_bus

    async def notify(self, exchange_rate: ExchangeRate) -> None:
        await super().notify(exchange_rate)
        await self._event_bus.create_event(exchange_rate)


def main():
    config = get_exchange_monitor_config()
    configure_logging(config.log_level)

    observers: list[ExchangeObserver] = [
        CoingeckoObserver(
            config=CoingeckoConfig(
                target_currencies=[
                    ("USD", "BTC"),
                    ("USD", "ETH"),
                    ("USD", "RUB"),
                    ("USDT", "USD"),
                ],
            )
        ),
    ]

    if (
        config.binance_api_key is not None
        and config.binance_api_secret is not None
    ):
        observers.append(
            BinanceObserver(
                config=BinanceConfig(
                    api_key=config.binance_api_key,
                    api_secret=config.binance_api_secret,
                    target_currencies=[
                        ("BTC", "USDT"),
                        ("ETC", "USDT"),
                        ("BTC", "RUB"),
                        ("ETC", "RUB"),
                    ],
                )
            )
        )

    event_bus = get_rabbitmq("exchange-rate", config.rabbitmq_uri)

    loop = asyncio.get_event_loop()

    loop.create_task(event_bus.startup(observe=False))
    exchange_controller = ExchangeUpdateMonitor(
        *observers,
        event_bus=event_bus,
    )
    loop.create_task(exchange_controller.control())

    loop.run_forever()


if __name__ == "__main__":
    main()
