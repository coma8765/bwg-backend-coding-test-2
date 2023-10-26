import asyncio
from logging import getLogger, basicConfig, DEBUG

from binance.client import AsyncClient
from binance.streams import BinanceSocketManager

api_key = "C542C1740D748AA85F485570A9E95B78C42DAEE75BF4FE73732D043793F0973A"
api_secret = "8D4535C629E2F054615872BC945223011CA3D1EE0B0718E8399A680F94204459"
symbols = (
    # "BTCUSDT",
    # "ETHUSDT",
    # "USDTTRCUSDT",
    # "USDTERCUSDT",
    # "USDTRUB",
    "BTCRUB",
    # "ETHRUB",
    # "USDTTRCRUB",
    # "USDTERCRUB",
)

logger = getLogger()


async def main():
    logger.info("start init")
    client = await AsyncClient.create(api_key, api_secret, )
    print(await client.get_margin_asset(asset="BNB"))
    # USDTTRC
    # USDTERC
    bm = BinanceSocketManager(client, user_timeout=10)

    logger.info("create sockets")
    sockets = tuple(
        bm.trade_socket(symbol)
        for symbol in symbols
    )
    print(sockets)
    return

    logger.info("start walk")
    while True:
        for socket in sockets:
            logger.debug("get info about socket")

            print(socket.ws_state)
            async with socket as tscm:
                res = await tscm.recv()
                print(res)


# basicConfig(level=DEBUG)
asyncio.run(main())
