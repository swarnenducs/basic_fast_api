"""SQLAlchemy engine / session factory.

SQL backend is selected by `MLAPI_SQL_BACKEND`:
  - sqlite     local file `sqlite:///./ml_api.db` (default)
  - azure_sql  Azure SQL Database via mssql+pyodbc
"""

from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.models import MLTransaction


class SqlConnection:
    def __init__(self):
        url = self._build_url()
        connect_args = {}
        if settings.sql_backend == "sqlite" or url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        self._engine = create_engine(url, connect_args=connect_args)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def _build_url(self) -> str:
        """Implement your code"""
        if settings.sql_backend == "azure_sql":
            if settings.azure_sql_connection_string:
                return settings.azure_sql_connection_string
            user = quote_plus(settings.azure_sql_username)
            password = quote_plus(settings.azure_sql_password)
            driver = quote_plus(settings.azure_sql_driver)
            server = settings.azure_sql_server
            database = settings.azure_sql_database
            return (
                f"mssql+pyodbc://{user}:{password}@{server}:1433/{database}"
                f"?driver={driver}&Encrypt=yes&TrustServerCertificate=no"
            )
        return settings.sql_connection_string

    def get_engine(self):
        """Implement your code"""
        return self._engine

    def get_session(self) -> Session:
        """Implement your code"""
        return self._session_factory()

    def create_tables(self):
        """Implement your code"""
        Base.metadata.create_all(bind=self._engine)

    def save_request_response(
        self,
        session: Session,
        request_payload: dict,
        response_payload: dict,
        x_id: str,
        ml_model_version: str,
    ) -> MLTransaction:
        """Implement your code"""
        row = MLTransaction(
            x_id=x_id,
            request_payload=request_payload,
            response_payload=response_payload,
            ml_model_version=ml_model_version,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row
