from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Never

from src.adapters.queue.models import Event


class EventBus(ABC):
    __slots__ = ("_channel", "_handlers")

    _handlers: list[Callable[[Event], Coroutine[None, None, Never]]]

    def __init__(self, channel: str):
        self._channel = channel
        self._handlers = list()  # type: ignore

    def on_event(
        self, handler: Callable[[Event], Coroutine[None, None, Never]]
    ):
        self._handlers.append(handler)

    async def emit(self, event: Event[Any]):
        for handler in self._handlers:
            await handler(event)

    @abstractmethod
    async def create_event(self, data: Any):
        pass

    @abstractmethod
    async def startup(self):
        pass
