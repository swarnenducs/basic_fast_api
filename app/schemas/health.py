"""Health check schema."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check payload."""

    status: str = "ok"
    app_name: str
    ml_model_version: str
    environment: str
    sql_backend: str
