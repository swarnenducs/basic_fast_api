"""Health check route."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        ml_model_version=settings.ml_model_version,
        environment=settings.app_env,
        sql_backend=settings.sql_backend,
    )
