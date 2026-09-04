"""FastAPI dependency injection.

Singletons are bound on app.state at startup. Route providers take Request
and resolve from that request's app. DB session is request-scoped (yield).
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session

from app.services.blob_download import BlobDownload
from app.services.mcp_invoke import MCPInvoke
from app.services.ml_model_invoke import MLModelInvoke
from app.services.ml_model_manager import MLModelManagerFromBlob
from app.services.rest_client import RestConsumeClient
from app.services.sql_connection import SqlConnection


def init_app_dependencies(app: FastAPI) -> None:
    """Attach class-level service instances to the FastAPI app."""
    app.state.sql_connection = SqlConnection()
    app.state.rest_client = RestConsumeClient()
    app.state.blob_download = BlobDownload()
    app.state.ml_model_invoke = MLModelInvoke()
    app.state.ml_model_manager = MLModelManagerFromBlob()
    app.state.mcp_invoke = MCPInvoke()


def get_sql_connection(request: Request) -> SqlConnection:
    return request.app.state.sql_connection


def get_db(request: Request) -> Generator[Session, None, None]:
    session = request.app.state.sql_connection.get_session()
    try:
        yield session
    finally:
        session.close()


def get_rest_client(request: Request) -> RestConsumeClient:
    return request.app.state.rest_client


def get_blob_download(request: Request) -> BlobDownload:
    return request.app.state.blob_download


def get_ml_model_invoke(request: Request) -> MLModelInvoke:
    return request.app.state.ml_model_invoke


def get_ml_model_manager(request: Request) -> MLModelManagerFromBlob:
    return request.app.state.ml_model_manager


def get_mcp_invoke(request: Request) -> MCPInvoke:
    return request.app.state.mcp_invoke


SqlConnectionDep = Annotated[SqlConnection, Depends(get_sql_connection)]
DbSessionDep = Annotated[Session, Depends(get_db)]
RestClientDep = Annotated[RestConsumeClient, Depends(get_rest_client)]
BlobDownloadDep = Annotated[BlobDownload, Depends(get_blob_download)]
MLModelInvokeDep = Annotated[MLModelInvoke, Depends(get_ml_model_invoke)]
MLModelManagerDep = Annotated[MLModelManagerFromBlob, Depends(get_ml_model_manager)]
MCPInvokeDep = Annotated[MCPInvoke, Depends(get_mcp_invoke)]
