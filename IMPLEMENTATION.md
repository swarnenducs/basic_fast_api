# Basic implementation document

This document describes the scaffold. Service methods are class-level hooks. Real REST, blob, MCP, and ML scoring logic is not implemented yet.

## Layout

```
app/
  main.py
  core/
    config.py          Dynaconf + Pydantic BaseSettings
    dependency.py      FastAPI Request-scoped Depends
  routers/
    health.py          GET /health
    ml.py              POST /api/v1/ml/invoke
  services/
    rest_client.py
    blob_download.py
    sql_connection.py  sqlite | azure_sql
    ml_model_invoke.py
    ml_model_manager.py
  mcp_invoke.py         FastMCP generic invoke (config-driven)
  schemas/
    request.py
    response.py
    health.py
  db/
    base.py
    models.py          MLTransaction (x_id)
azure_web_app/         Azure App Service JSON generated from .env
postman/
samples/
settings.toml
.env.example
```

## Configuration

`app/core/config.py` loads Dynaconf (`settings.toml`, `.secrets.toml`, env prefix `MLAPI`) and maps values into a Pydantic `Settings(BaseSettings)` instance.

Important keys:

| Key | Purpose |
| --- | --- |
| `ML_MODEL_VERSION` | Model version used at startup and persisted on each invoke |
| `SQL_BACKEND` | `sqlite` (default) or `azure_sql` |
| `SQL_CONNECTION_STRING` | SQLite URL when backend is sqlite |
| `AZURE_SQL_SERVER` | Azure SQL host (`*.database.windows.net`) |
| `AZURE_SQL_DATABASE` | Azure SQL database name |
| `AZURE_SQL_USERNAME` | Azure SQL user |
| `AZURE_SQL_PASSWORD` | Azure SQL password |
| `AZURE_SQL_DRIVER` | ODBC driver name (default `ODBC Driver 18 for SQL Server`) |
| `AZURE_SQL_CONNECTION_STRING` | Optional full SQLAlchemy URL override |
| `BLOB_ACCOUNT_URL` | Blob account (hook only) |
| `BLOB_CONTAINER_NAME` | Container for the model artifact |
| `BLOB_MODEL_PATH` | Blob path / filename of the model |
| `REST_CLIENT_BASE_URL` | Outbound REST client base URL |
| `MCP_ENDPOINT` | FastMCP server URL |
| `MCP_TRANSPORT` | `http` / `sse` / `stdio` |
| `MCP_SERVER_NAME` | Logical MCP server name |
| `MCP_TOOL_NAME` | Default tool for the generic invoke |
| `MCP_TIMEOUT_SECONDS` | FastMCP call timeout |

## Dependency injection

Singletons are created on startup and stored on `app.state`. Each `get_*` provider takes FastAPI `Request` and reads from `request.app.state`. The DB session is yielded per request and closed in `finally`.

Routes use FastAPI `Annotated` aliases (`RestClientDep`, `DbSessionDep`, …) instead of repeating `Depends(...)`.

## Startup

`@app.on_event("startup")` in `app/main.py`:

1. `init_app_dependencies(app)` binds service instances on `app.state`
2. `SqlConnection.create_tables()`
3. `MLModelManagerFromBlob.check_and_evaluate_ml_model()` which calls `BlobDownload.download_blob()`

## Service hooks

Each class lives in `app/services/`:

```python
class RestConsumeClient:
    def consume(self, url=None, payload=None):
        """Implement your code"""

class BlobDownload:
    def download_blob(self, container=None, blob_name=None):
        """Implement your code"""

class SqlConnection:
    def get_engine(self): ...
    def get_session(self): ...
    def create_tables(self): ...
    def save_request_response(self, session, request_payload, response_payload, x_id, ml_model_version): ...

class MLModelInvoke:
    def invoke_ml_model(self, _):
        """Implement your code"""

class MLModelManagerFromBlob:
    def check_and_evaluate_ml_model(self):
        """Implement your code"""

class MCPInvoke:
    async def invoke_mcp(self, tool_name=None, arguments=None, resource_uri=None):
        # FastMCP Client; endpoint/tool/timeout from config
```

`MLModelInvoke.invoke_ml_model` currently returns `STATIC_ML_RESPONSE`. `SqlConnection.save_request_response` writes request JSON, response JSON, model version, and `x_id`.

## ML invoke flow

`POST /api/v1/ml/invoke`

1. Validate body as `MLModelRequest`
2. `MCPInvoke.invoke_mcp(arguments=payload)` via FastMCP (config-driven; skipped if endpoint empty)
3. `RestConsumeClient.consume()`
4. `MLModelInvoke.invoke_ml_model(payload)` → static `MLModelResponse`
5. Generate UUID `x_id`
6. Persist request + response via SQLAlchemy
7. Return static response body; set `X-Id` header

## Persistence

Table `ml_transactions`:

- `x_id` (UUID string, PK)
- `request_payload` (JSON)
- `response_payload` (JSON)
- `ml_model_version` (string)
- `created_at` (datetime)

Default backend is SQLite. Set `MLAPI_SQL_BACKEND=azure_sql` plus Azure SQL credentials (or `MLAPI_AZURE_SQL_CONNECTION_STRING`) to persist on Azure SQL Database. `pyodbc` and ODBC Driver 18 are required for that option.

## Swagger

FastAPI OpenAPI is enabled:

- `/docs` Swagger UI
- `/redoc` ReDoc
- `/openapi.json`

## Postman

Import `postman/ML_API.postman_collection.json` and `postman/ML_API.postman_environment.json`. Variable `baseUrl` defaults to `http://127.0.0.1:8000`.

## Azure Web App

`azure_web_app/appsettings.json` is the Azure App Service Application Settings array, generated from `.env`:

```bash
python azure_web_app/generate_appsettings.py
```

`azure_web_app/webapp.config.json` holds Linux Python runtime and the uvicorn startup command.
