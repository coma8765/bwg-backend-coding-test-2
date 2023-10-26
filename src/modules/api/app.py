"""Application for serving exchange rate data


"""
import asyncio

from fastapi import FastAPI

from src.adapters.queue.third_party.rabbitmq.queue import get_rabbitmq
from src.core import add_fastapi_prometheus, configure_logging, get_api_config
from src.modules.api.exchange_rate_store import get_exchange_rate_store
from src.modules.api.routes import router

config = get_api_config()
configure_logging(config.log_level)


async def bootstrap_app(_: FastAPI):
    exchange_update_queue = get_rabbitmq(
        config.rabbitmq_exchange_rate_channel,
        config.rabbitmq_uri,
    )

    get_exchange_rate_store(  # Need for pre-init
        exchange_update_queue,
        enable_metrics=True,
    )

    asyncio.create_task(exchange_update_queue.startup(observe=True))

    yield


app = FastAPI(lifespan=bootstrap_app)
add_fastapi_prometheus(app)
app.include_router(router)
