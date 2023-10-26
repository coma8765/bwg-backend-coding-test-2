import json
from dataclasses import dataclass, field
from http import HTTPStatus, HTTPMethod
from typing import Union
from uuid import UUID, uuid4


@dataclass
class _BaseRequest:
    url: str
    method: HTTPMethod = HTTPMethod.GET
    id: UUID = field(default_factory=uuid4)


@dataclass
class Request(_BaseRequest):
    data: str | dict | None = None
    _response: Union["Response", None] = None

    @property
    def body(self) -> bytes | None:
        if self.data is not None:
            data = json.dumps(self.data)
            return data.encode()
        return None


@dataclass
class Response(_BaseRequest):
    status: HTTPStatus = HTTPStatus.OK
    body: bytes | None = None
    _json: str | int | dict | None = None

    @property
    def json(self) -> int | dict | str | None:
        if self.body is not None:
            if self._json is None:
                self._json = json.loads(self.body)
            return self._json

        return None
