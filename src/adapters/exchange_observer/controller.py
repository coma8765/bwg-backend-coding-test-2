"""Controller for exchange rate observers

Abstract:
    Change current observer if they don't respond
"""
import asyncio
import time
from abc import ABC
from asyncio import sleep
from logging import Logger

from src.adapters.exchange_observer.abc import (
    ExchangeObservable,
    ExchangeObserver,
)
from src.adapters.exchange_observer.models import ExchangeRate
from src.core import get_logger

KEEP_ALIVE_TIME = 5  # TODO: @coma8765 recommend use exponential timeout


class ExchangeUpdateController(ExchangeObservable, ABC):
    __slots__ = ("_current_work", "_recent_update_time", "_logger")
    _current_work: int
    _recent_update_time: int
    _logger: Logger

    def __init__(self, *observables: ExchangeObserver):
        super().__init__(*observables)
        self._logger = get_logger("exchange-controller")
        self._current_work = 0

    async def _manage(self):
        self._logger.info(
            "update alive observer to %s",
            self._observables[self._current_work],
        )

        self._recent_update_time = int(time.time())

        observer: ExchangeObserver
        fail: bool = False
        for index, observer in enumerate(self._observables):
            if index != self._current_work:
                await observer.stop()
            else:
                if not await observer.start():
                    fail = True

        if fail:
            self._logger.critical(
                "fail to startup observer, sleep 1s and change again"
            )
            await sleep(1)  # TODO: @coma8765 change to exponential delay
            await self.change_observer()

    async def change_observer(self):
        if self._current_work + 1 == len(self._observables):
            self._current_work = 0
        else:
            self._current_work += 1

        await self._manage()

    async def control(self):
        loop = asyncio.get_running_loop()

        await self._manage()
        while loop.is_running():
            if self._recent_update_time + KEEP_ALIVE_TIME < time.time():
                self._logger.critical("observer not responding, change")
                await self.change_observer()
            await sleep(5)

    async def notify(self, exchange_rate: ExchangeRate) -> None:
        self._recent_update_time = int(time.time())
