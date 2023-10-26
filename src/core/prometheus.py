"""Prometheus metrics utils"""
from functools import lru_cache

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


@lru_cache()
def get_instrumentator() -> Instrumentator:
    return Instrumentator()


def add_fastapi_prometheus(app: FastAPI):
    instrumentator = get_instrumentator()
    instrumentator.instrument(app).expose(app)


__all__ = ["add_fastapi_prometheus"]
