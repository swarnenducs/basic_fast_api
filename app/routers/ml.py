"""ML invoke route."""

from uuid import uuid4

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependency import (
    get_db,
    get_mcp_invoke,
    get_ml_model_invoke,
    get_rest_client,
    get_sql_connection,
)
from app.schemas.request import MLModelRequest
from app.schemas.response import MLModelResponse
from app.services.mcp_invoke import MCPInvoke
from app.services.ml_model_invoke import MLModelInvoke
from app.services.rest_client import RestConsumeClient
from app.services.sql_connection import SqlConnection

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.post("/invoke", response_model=MLModelResponse)
async def invoke_ml_model(
    payload: MLModelRequest,
    response: Response,
    rest_client: RestConsumeClient = Depends(get_rest_client),
    ml_invoke: MLModelInvoke = Depends(get_ml_model_invoke),
    mcp: MCPInvoke = Depends(get_mcp_invoke),
    sql_conn: SqlConnection = Depends(get_sql_connection),
    db: Session = Depends(get_db),
):
    await mcp.invoke_mcp(arguments=payload.model_dump(mode="json"))
    rest_client.consume()
    ml_response = ml_invoke.invoke_ml_model(payload)

    x_id = str(uuid4())
    sql_conn.save_request_response(
        session=db,
        request_payload=payload.model_dump(mode="json"),
        response_payload=ml_response.model_dump(mode="json"),
        x_id=x_id,
        ml_model_version=settings.ml_model_version,
    )
    response.headers["X-Id"] = x_id
    return ml_response
