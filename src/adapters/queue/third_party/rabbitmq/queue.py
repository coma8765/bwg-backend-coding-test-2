import asyncio
import dataclasses
import json
from asyncio import sleep
from functools import lru_cache
from logging import Logger
from random import randint
from typing import TypeVar, Any

from aio_pika import connect, Message
from aio_pika.abc import (
    AbstractConnection,
    AbstractChannel,
    AbstractExchange,
    ExchangeType,
    AbstractIncomingMessage,
    DeliveryMode,
)

from src.adapters.queue.abc import EventBus
from src.adapters.queue.models import Event
from src.core import get_logger, configure_logging


RABBITMQ_RECONNECTION_MIN_DELAY = 1
RABBITMQ_RECONNECTION_MAX_DELAY = 15


# @lru_cache()
async def _get_rabbit_mq(connection_uri: str) -> AbstractConnection:
    logger = get_logger("third-party.rabbitmq")

    logger.debug("create connection")
    delay: float = RABBITMQ_RECONNECTION_MIN_DELAY
    while True:  # Exponential backoff
        try:
            connection = await connect(connection_uri)
            await connection.__aenter__()  # pylint: disable=C2801
            return connection
        except (ConnectionError, KeyError):
            logger.warning("fail create connection, sleep %ss", delay)
            await sleep(delay)

        delay += delay * randint(1, 100) * 0.01
        delay = min(delay, RABBITMQ_RECONNECTION_MAX_DELAY)


class RabbitMQEventBus(EventBus):
    __slots__ = (
        "_connection_uri",
        "_connection",
        "_channel_instance",
        "_exchange",
        "_logger",
    )
    _logger: Logger
    _connection_uri: str
    _connection: AbstractConnection
    _channel_instance: AbstractChannel
    _exchange: AbstractExchange

    def __init__(self, channel: str, connection_uri: str):
        self._logger = get_logger("third-party.rabbitmq")
        print(channel)
        super().__init__(channel)
        self._connection_uri = connection_uri

    async def startup(self, observe: bool = False):
        self._logger.info("startup")
        self._connection = await _get_rabbit_mq(self._connection_uri)
        self._channel_instance = await self._connection.channel()
        self._exchange = await self._channel_instance.declare_exchange(
            self._channel, ExchangeType.FANOUT
        )

        if observe:
            asyncio.create_task(self._observe_messages())

    async def create_event(self, data: Any):
        event = Event(self._channel, data=data)

        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(event)

        message = Message(
            json.dumps(data, default=str).encode(),
            delivery_mode=DeliveryMode.NOT_PERSISTENT,
        )

        self._logger.debug(
            "create new event channel '%s' with data '%s'",
            self._channel,
            data,
        )
        await self._exchange.publish(message, routing_key="")

    async def _observe_messages(self):
        queue = await self._channel_instance.declare_queue(exclusive=True)

        await queue.bind(self._exchange)
        self._logger.info("start listen events channel '%s'", self._channel)

        async with queue.iterator() as iter_:
            message: AbstractIncomingMessage
            async for message in iter_:
                async with message.process():
                    data = json.loads(message.body)
                    self._logger.debug('got new message "%s"', data)
                    await self.emit(Event(**data))


@lru_cache()
def get_rabbitmq(*args, **kwargs):
    return RabbitMQEventBus(*args, **kwargs)


if __name__ == "__main__":
    configure_logging("DEBUG")
    rabbit_ = RabbitMQEventBus("test", "amqp://guest:guest@127.0.0.1/")

    @rabbit_.on_event
    async def test_(event: Event):
        print(event)

    loop_ = asyncio.new_event_loop()
    loop_.create_task(rabbit_.startup(observe=True))
    # loop_.create_task(rabbit_.create_event({"example": "d"}))
    loop_.run_forever()


__all__ = ["RabbitMQEventBus", "get_rabbitmq"]
