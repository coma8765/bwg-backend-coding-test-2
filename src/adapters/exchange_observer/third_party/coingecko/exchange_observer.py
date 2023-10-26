import asyncio
from asyncio import sleep
from functools import lru_cache
from http import HTTPStatus
from logging import Logger

from binance import AsyncClient, BinanceSocketManager
from binance.streams import ReconnectingWebsocket

from src.adapters.exchange_observer.abc import (
    ExchangeObserver,
)
from src.adapters.exchange_observer.models import ExchangeRate
from src.adapters.exchange_observer.third_party.coingecko.config import (
    CoingeckoConfig,
)
from src.adapters.http import make_request
from src.adapters.http.abc import RequestFail
from src.core import get_logger, configure_logging

_COINS_ENDPOINT_FORMATTED = (
    "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies={}"
)


def _make_get_coin_to_quotes_url(
    target_currency: str,
    quote_currencies: str,
):
    return _COINS_ENDPOINT_FORMATTED.format(target_currency, quote_currencies)


class CoingeckoObserver(ExchangeObserver):
    __slots__ = (
        "_client",
        "_sockets",
        "_logger",
        "_config",
    )

    _client: AsyncClient
    _socket_manager: BinanceSocketManager
    _logger: Logger
    _sockets: ReconnectingWebsocket
    _config: CoingeckoConfig

    def __init__(
        self,
        config: CoingeckoConfig,
    ):
        super().__init__()
        self._config = config
        self._logger = get_logger("third-party.coingecko")

    async def _observe_pair(
        self,
        currencies: tuple[str, str],
    ):
        loop = asyncio.get_running_loop()

        self._logger.info(
            "start observe target currencies '%s'",
            "-".join(currencies),
        )

        url = _make_get_coin_to_quotes_url(*currencies)

        while loop.is_running() and not self._stopped:
            request = make_request(url)

            try:
                response = await request.make()
            except RequestFail:
                self._logger.warning("fail update data, try again after 0.5s")
                await sleep(0.5)
                # TODO: @coma8765 change exponential wait time
                continue

            self._logger.debug(
                "got new exchange data (%s)",
                response.json,
            )

            if response.status != HTTPStatus.OK:
                # TODO: handle failed exception
                self._logger.critical(
                    "fail update data "
                    "(request %s, url %s, status %s, body %s), "
                    "try again after 0.5s ",
                    response.id,
                    response.url,
                    response.status,
                    response.body,
                )
                await sleep(0.5)
                continue

            exchange_rate = ExchangeRate(
                exchanger="coingecko",
                currencies=currencies,
                value=float(
                    # TODO: add TypedDict for fix mypy error
                    response.json[currencies[0]][currencies[1]]  # type: ignore
                ),
            )

            await self.notify_observers(exchange_rate)
            await sleep(self._config.delay)

    async def _observe(self):
        cors = tuple(
            self._observe_pair(pair) for pair in self._config.target_currencies
        )

        await asyncio.gather(*cors)

    async def startup(self) -> bool:
        self._logger.debug("startup observer")
        asyncio.create_task(self._observe())
        return True  # TODO: @coma8765 add ping request for health check


@lru_cache()
def get_coingecko_observer(config: CoingeckoConfig) -> CoingeckoObserver:
    return CoingeckoObserver(config)


if __name__ == "__main__":
    configure_logging("DEBUG")

    observer = CoingeckoObserver(
        config=CoingeckoConfig(
            target_currencies=[("usd", "btc"), ("usd", "eth")],
        )
    )

    loop_ = asyncio.new_event_loop()
    loop_.create_task(observer.startup())
    loop_.run_forever()

__all__ = ["get_coingecko_observer", "CoingeckoObserver"]
