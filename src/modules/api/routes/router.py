"""Application endpoints"""
from fastapi import APIRouter

from src.modules.api.routes import v1

router = APIRouter()
router.include_router(v1.router, prefix="/v1")

__all__ = ["router"]
