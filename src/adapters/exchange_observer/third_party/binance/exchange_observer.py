import asyncio
from functools import lru_cache
from logging import Logger

from aiohttp import ClientConnectorError
from binance import AsyncClient, BinanceSocketManager
from binance.streams import ReconnectingWebsocket

from src.adapters.exchange_observer.abc import ExchangeObserver
from src.adapters.exchange_observer.models import ExchangeRate
from src.adapters.exchange_observer.third_party.binance.config import (
    BinanceConfig,
)
from src.core import configure_logging, get_logger


class BinanceObserver(ExchangeObserver):
    __slots__ = (
        "_config",
        "_client",
        "_sockets",
        "_logger",
    )

    _config: BinanceConfig
    _client: AsyncClient
    _socket_manager: BinanceSocketManager
    _logger: Logger
    _sockets: ReconnectingWebsocket

    def __init__(self, config: BinanceConfig):
        super().__init__()
        self._config = config
        self._logger = get_logger("third-party.binance-ws")
        self._client = None
        self._sockets = None

    async def _observe_socket(
        self,
        currencies: tuple[str, str],
        socket: ReconnectingWebsocket,
    ):
        loop = asyncio.get_running_loop()

        self._logger.info(
            "start observe %s (%s)",
            "-".join(currencies),
            socket,
        )

        while loop.is_running() and not self._stopped:
            async with socket as tscm:
                res = await tscm.recv()
                if "p" not in res:
                    continue

                data = ExchangeRate("binance", currencies, value=res["p"])
                self._logger.debug("got currency data '%s'", data)
                await self.notify_observers(data)

        await socket.__aexit__(None, None, None)

    async def _observe(self):
        self._logger.debug("start observe")
        cors = tuple(
            self._observe_socket(currencies, socket)
            for currencies, socket, in zip(
                self._config.target_currencies,
                self._sockets,
            )
        )
        await asyncio.gather(*cors)

    async def _create_websockets(self):
        if self._sockets:
            for socket in self._sockets:
                await socket.__aexit__(None, None, None)

        socket_manager = BinanceSocketManager(
            self._client,
            user_timeout=self._config.timeout,
        )

        self._sockets = tuple(
            socket_manager.trade_socket("".join(currency))
            for currency in self._config.target_currencies
        )

    async def startup(self) -> bool:
        self._logger.debug("startup observer")

        if self._client is not None:
            await self._client.close_connection()

        try:
            self._client = await AsyncClient.create(
                self._config.api_key,
                self._config.api_secret,
            )
            await self._create_websockets()
        except (ClientConnectorError, TimeoutError, OSError):
            self._logger.critical("network fail")
            return False

        asyncio.create_task(self._observe())
        return True


@lru_cache()
def get_binance_observer(config: BinanceConfig) -> BinanceObserver:
    return BinanceObserver(config)


if __name__ == "__main__":
    configure_logging("DEBUG")

    observer = BinanceObserver(
        config=BinanceConfig(
            api_key="C542C1740D748AA85F485570A9E95B78C42DAEE75BF4FE73732D043793F0973A",
            api_secret="8D4535C629E2F054615872BC945223011CA3D1EE0B0718E8399A680F94204459",
            target_currencies=[("BTC", "USDT"), ("ETC", "USDT")],
        )
    )

    loop_ = asyncio.new_event_loop()
    loop_.create_task(observer.startup())
    loop_.run_forever()

__all__ = ["get_binance_observer", "BinanceObserver"]
