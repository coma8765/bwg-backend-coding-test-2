from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.modules.api.depends import get_exchange_rate_store
from src.modules.api.exchange_rate_store import (
    ExchangeRateStore,
    DataNotExist,
    ExchangeRates,
)

router = APIRouter()


@router.get("/")
async def get_courses(
    exchange_rate_store: ExchangeRateStore = Depends(
        get_exchange_rate_store, use_cache=True
    ),
) -> ExchangeRates:
    try:
        return exchange_rate_store.exchange_rates
    except DataNotExist as exc:
        raise HTTPException(
            HTTPStatus.SERVICE_UNAVAILABLE,
            "please wait for a while to bootstrap the app",
        ) from exc


__all__ = ["router"]
