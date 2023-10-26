import asyncio
from http import HTTPStatus
from logging import Logger

import aiohttp
from aiohttp import ClientTimeout

from src.adapters.http.abc import HTTPRequest, RequestFail
from src.adapters.http.models import Response
from src.core import get_logger


class AioHTTP(HTTPRequest):
    _logger: Logger = get_logger("third-party.aiohttp")

    async def _make(self) -> Response:
        self._logger.debug(
            "request '%s' started (url %s)",
            self.id,
            self.url,
        )
        try:
            async with (
                aiohttp.ClientSession(timeout=ClientTimeout(1)) as session
            ):
                async with session.request(self.method, self.url) as response:
                    res = Response(
                        id=self.id,
                        url=self.url,
                        method=self.method,
                        status=HTTPStatus(response.status),
                        body=await response.content.read(),
                    )

                    self._logger.debug(
                        "request '%s' completed (url %s, status %s)",
                        self.id,
                        self.url,
                        res.status,
                    )

                    return res
        except (ConnectionError, TimeoutError, OSError) as e:
            self._logger.critical("fail http request")
            raise RequestFail from e


if __name__ == "__main__":
    rq = AioHTTP("https://httpbin.org/get")
    res = asyncio.run(rq.make())

    print("status", res.status)
    print("json", res.json)
