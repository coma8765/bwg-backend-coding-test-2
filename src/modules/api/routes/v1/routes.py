from fastapi import APIRouter

from src.modules.api.routes.v1 import courses

router = APIRouter()

router.include_router(courses.router, prefix="/courses")

__all__ = ["router"]
