from abc import ABC, abstractmethod

from src.adapters.exchange_observer.models import ExchangeRate


class ExchangeObservable(ABC):
    __slots__ = ("_observables",)
    _observables: tuple["ExchangeObserver", ...]

    def __init__(self, *observables: "ExchangeObserver"):
        for observable in observables:
            observable.register_observer(self)

        self._observables = observables

    @abstractmethod
    async def notify(self, exchange_rate: ExchangeRate) -> None:
        pass


class ExchangeObserver(ABC):
    __slots__ = ("_observers", "_stopped")
    _observers: list[ExchangeObservable]
    _stopped: bool

    def __init__(self):
        self._observers = []
        self._stopped = False

    @abstractmethod
    async def startup(self) -> bool:
        pass

    async def stop(self):
        self._stopped = True

    async def start(self):
        if self._stopped is True:
            self._stopped = False

            return await self.startup()
        return True

    def register_observer(self, observer: ExchangeObservable):
        self._observers.append(observer)

    async def notify_observers(self, exchange_rate: ExchangeRate):
        for obs in self._observers:
            await obs.notify(exchange_rate)
