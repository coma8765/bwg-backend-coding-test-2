from http import HTTPMethod

from src.adapters.http.abc import HTTPRequest
from src.adapters.http.third_party.aiohttp.http import AioHTTP


def make_request(
    url: str,
    method: HTTPMethod = HTTPMethod.GET,
    data: str | dict | None = None,
) -> HTTPRequest:
    return AioHTTP(url=url, method=method, data=data)


__all__ = ["make_request"]
