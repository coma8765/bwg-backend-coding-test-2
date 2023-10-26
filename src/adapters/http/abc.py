from abc import ABC, abstractmethod

from src.adapters.http.models import Request, Response


class RequestFail(ConnectionError):
    pass


class HTTPRequest(Request, ABC):
    """
    TODO:
        * add accepted exceptions and handling fails in request
    """

    __slots__ = ()
    _response: Response | None = None

    async def make(self) -> Response:
        """Makes request

        :raise RequestFail: if request was failed
        :return: server response for request
        """
        if self._response is None:
            self._response = await self._make()

        return self._response

    @abstractmethod
    async def _make(self) -> Response:
        pass
