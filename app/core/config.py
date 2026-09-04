"""Application configuration.

Dynaconf loads layered files (`settings.toml`, `.secrets.toml`) and env vars.
Pydantic BaseSettings exposes a typed settings object used across the app.
"""

from typing import Literal

from dynaconf import Dynaconf
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

dynaconf_settings = Dynaconf(
    envvar_prefix="MLAPI",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
    env_switcher="ENV_FOR_DYNACONF",
)


class Settings(BaseSettings):
    """Typed runtime settings. Env vars override Dynaconf file values."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MLAPI_",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default_factory=lambda: dynaconf_settings.get("APP_NAME", "ML API"))
    app_env: str = Field(default_factory=lambda: dynaconf_settings.get("APP_ENV", "development"))
    ml_model_version: str = Field(
        default_factory=lambda: dynaconf_settings.get("ML_MODEL_VERSION", "v1.0.0")
    )
    sql_backend: Literal["sqlite", "azure_sql"] = Field(
        default_factory=lambda: dynaconf_settings.get("SQL_BACKEND", "sqlite")
    )
    sql_connection_string: str = Field(
        default_factory=lambda: dynaconf_settings.get(
            "SQL_CONNECTION_STRING", "sqlite:///./ml_api.db"
        )
    )
    azure_sql_server: str = Field(
        default_factory=lambda: dynaconf_settings.get("AZURE_SQL_SERVER", "")
    )
    azure_sql_database: str = Field(
        default_factory=lambda: dynaconf_settings.get("AZURE_SQL_DATABASE", "")
    )
    azure_sql_username: str = Field(
        default_factory=lambda: dynaconf_settings.get("AZURE_SQL_USERNAME", "")
    )
    azure_sql_password: str = Field(
        default_factory=lambda: dynaconf_settings.get("AZURE_SQL_PASSWORD", "")
    )
    azure_sql_driver: str = Field(
        default_factory=lambda: dynaconf_settings.get(
            "AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server"
        )
    )
    azure_sql_connection_string: str = Field(
        default_factory=lambda: dynaconf_settings.get("AZURE_SQL_CONNECTION_STRING", "")
    )
    blob_account_url: str = Field(
        default_factory=lambda: dynaconf_settings.get("BLOB_ACCOUNT_URL", "")
    )
    blob_container_name: str = Field(
        default_factory=lambda: dynaconf_settings.get("BLOB_CONTAINER_NAME", "ml-models")
    )
    blob_model_path: str = Field(
        default_factory=lambda: dynaconf_settings.get(
            "BLOB_MODEL_PATH", "models/pricing_model.pkl"
        )
    )
    rest_client_base_url: str = Field(
        default_factory=lambda: dynaconf_settings.get(
            "REST_CLIENT_BASE_URL", "http://localhost:8000"
        )
    )
    mcp_endpoint: str = Field(default_factory=lambda: dynaconf_settings.get("MCP_ENDPOINT", ""))
    mcp_transport: str = Field(
        default_factory=lambda: dynaconf_settings.get("MCP_TRANSPORT", "http")
    )
    mcp_server_name: str = Field(
        default_factory=lambda: dynaconf_settings.get("MCP_SERVER_NAME", "")
    )
    mcp_tool_name: str = Field(default_factory=lambda: dynaconf_settings.get("MCP_TOOL_NAME", ""))
    mcp_timeout_seconds: float = Field(
        default_factory=lambda: dynaconf_settings.get("MCP_TIMEOUT_SECONDS", 30) or 30
    )

    @field_validator("sql_backend", mode="before")
    @classmethod
    def normalize_sql_backend(cls, value: str) -> str:
        if not value:
            return "sqlite"
        return str(value).strip().lower()


settings = Settings()
