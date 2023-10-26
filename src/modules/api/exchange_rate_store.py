from dataclasses import dataclass
from functools import lru_cache
from logging import Logger
from typing import Any

from prometheus_client import Counter

from src.adapters.exchange_observer.models import ExchangeRate
from src.adapters.queue.abc import EventBus
from src.adapters.queue.models import Event
from src.core import get_logger


@dataclass
class ExchangeRateShort:
    direction: str
    value: float


class DataNotExist(Exception):
    pass


@dataclass
class ExchangeRates:
    """
    {
      "exchanger": "binance",
      "courses": [
        {
          "direction": "BTC-USD",
          "value": 54000.000123
        }
      ]
    }
    """

    exchanger: str
    courses: list[ExchangeRateShort]


class ExchangeRateStore:
    """Stores exchange rates"""

    __slots__ = ("_logger", "_data", "_latest_exchanger", "_metric")
    _logger: Logger
    _data: dict[str, dict[tuple[str, str], ExchangeRate]]
    _latest_exchanger: str | None
    _metric: Counter | None

    def __init__(
        self,
        event_bus: EventBus,
        enable_metrics: bool = False,
    ):
        self._logger = get_logger("exchange-rate-store")
        event_bus.on_event(self._update_exchange_rate)

        self._latest_exchanger = None
        self._data = {}

        if enable_metrics:
            self._metric = Counter(
                "exchange_rate_updates",
                "Exchange rate updates.",
                labelnames=("exchanger", "currencies"),
            )

    def _set_data(self, exchange_rate: ExchangeRate):
        if self._metric:
            self._metric.labels(
                exchange_rate.exchanger, exchange_rate.currencies
            ).inc()

        if exchange_rate.exchanger not in self._data:
            self._data[exchange_rate.exchanger] = {}

        self._latest_exchanger = exchange_rate.exchanger
        exchanger_data = self._data[exchange_rate.exchanger]
        exchanger_data[exchange_rate.currencies] = exchange_rate

    async def _update_exchange_rate(self, event: Event[dict]):
        self._logger.debug("update data '%s'", event.data)

        exchange_rate = ExchangeRate(
            currencies=tuple(event.data.pop("currencies")),  # type: ignore
            **event.data,
        )

        self._set_data(exchange_rate)

    @property
    def exchange_rates(self) -> ExchangeRates:
        """Returns latest exchange rates
        :raise DataNotExist: if data doesn't exists
        :return: latest exchange rates
        """
        if self._latest_exchanger is None:
            raise DataNotExist

        latest_data = self._data[self._latest_exchanger]

        return ExchangeRates(
            self._latest_exchanger,
            [
                ExchangeRateShort(exchange.direction, exchange.value)
                for exchange in latest_data.values()
            ],
        )


@lru_cache()
def get_exchange_rate_store(*args, **kwargs) -> ExchangeRateStore:
    return ExchangeRateStore(*args, **kwargs)
