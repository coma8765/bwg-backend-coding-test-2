import asyncio
import logging
from logging import Logger, getLogger

from binance_ import AsyncClient, BinanceSocketManager
from binance_.streams import ReconnectingWebsocket
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

api_key = "C542C1740D748AA85F485570A9E95B78C42DAEE75BF4FE73732D043793F0973A"
api_secret = "8D4535C629E2F054615872BC945223011CA3D1EE0B0718E8399A680F94204459"
logging.basicConfig(level=logging.INFO)
symbols = (
    "BTCUSDT",
    "ETHUSDT",
    # "USDTTRCUSDT",
    # "USDTERCUSDT",
    # "BTC_RUB",
    # "ETH_RUB",
    # "USDTTRCRUB",
    # "USDTERCRUB",
)


class BinanceWebsocket:
    __slots__ = ("_data", "_client", "_bm", "_sockets", "_stop", "data",
                 "_logger",)
    _bm: BinanceSocketManager
    _client: AsyncClient
    _sockets: tuple[ReconnectingWebsocket]
    _stop: bool
    _logger: Logger

    def __init__(self):
        self._logger = getLogger("binance")
        self._logger.info("init binance")

    async def startup(self):
        self._logger.info("startup binance sockets")

        self._client = await AsyncClient.create(api_key, api_secret)
        self._bm = BinanceSocketManager(self._client)

        self._sockets = tuple(
            self._bm.trade_socket(symbol)
            for symbol in symbols
        )

        self._stop = False

    async def loop(self):
        while not self._stop:
            self._logger.warning("update binance")

            for socket in self._sockets:
                if self._stop:
                    break

                async with socket as tscm:
                    res = await tscm.recv()
                    print(res)

        self._logger.warning("Shutdown binance")

    async def shutdown(self):
        self._stop = True


binance = BinanceWebsocket()


async def _lifespan(_app: FastAPI):
    await binance.startup()

    asyncio.create_task(binance.loop())

    yield

    await binance.shutdown()


app = FastAPI(
    # lifespan=_lifespan,
)

current_etag = "4"


@app.get("/")
async def test(request: Request, response: Response):
    if request.headers["if-none-match"] == current_etag:
        response.status_code = 304
        return

    response.headers["ETag"] = current_etag
    return {"status": "success"}
