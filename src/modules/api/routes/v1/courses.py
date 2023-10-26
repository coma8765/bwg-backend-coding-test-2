"""Courses API endpoints"""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.modules.api.depends import get_exchange_rate_store
from src.modules.api.exchange_rate_store import DataNotExist, ExchangeRateStore

router = APIRouter()


# @dataclass
class ExchangeRateShort(BaseModel):
    direction: str
    value: float


class ExchangeRatesResponse(BaseModel):
    exchanger: str
    courses: list[ExchangeRateShort]


@router.get("/")
async def get_courses(
    exchange_rate_store: ExchangeRateStore = Depends(
        get_exchange_rate_store, use_cache=True
    ),
) -> ExchangeRatesResponse:
    try:
        return ExchangeRatesResponse(
            exchanger=exchange_rate_store.exchange_rates.exchanger,
            courses=[
                ExchangeRateShort(
                    direction=course.direction, value=course.value
                )
                for course in exchange_rate_store.exchange_rates.courses
            ],
        )
    except DataNotExist as exc:
        raise HTTPException(
            HTTPStatus.SERVICE_UNAVAILABLE,
            "please wait for a while to bootstrap the app",
        ) from exc


__all__ = ["router"]
