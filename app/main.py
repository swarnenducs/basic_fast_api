"""ML API entrypoint."""

from fastapi import FastAPI

from app.core.config import settings
from app.core.dependency import init_app_dependencies
from app.routers import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.ml_model_version,
    description=(
        "ML pricing API. Request schema is the incoming agreement/products payload. "
        "Response schema is cohort corridor pricing. Model artifacts are loaded from blob "
        "on startup using ML_MODEL_VERSION."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    init_app_dependencies(app)
    app.state.sql_connection.create_tables()
    app.state.ml_model_manager.check_and_evaluate_ml_model()
