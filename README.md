# ML API

Basic FastAPI service for ML pricing. Request and response follow the attached agreement/product schemas. The ML model version is read from env (`MLAPI_ML_MODEL_VERSION` / Dynaconf `ML_MODEL_VERSION`). On startup, `MLModelManagerFromBlob.check_and_evaluate_ml_model()` runs the blob process: it calls `BlobDownload.download_blob()` for the configured container and model path. Scoring is a stub and currently returns a static response.

## Request schema

`POST /api/v1/ml/invoke`

```json
{
  "agreement": {
    "agreement_num": "50002187",
    "contract_type": "0001",
    "total_revenue_12m": 245000.0,
    "sales_commitment": 50000.0,
    "class_of_trade": "AC,GP,HH",
    "valid_from_dt": "2026-01-01",
    "valid_to_dt": "2026-12-31",
    "request_type": "New Contract",
    "entity_type": "GPO"
  },
  "products": [
    {
      "prod_num": "1642201",
      "prod_desc": "AQUACEL AG FOAM 10X10CM (1X10PK) US",
      "product_franchise": "WOUND CARE",
      "prod_sub_grp_desc": "ADVANCED WOUND DRESSINGS",
      "list_price_ea": 42.50,
      "base6_ea": 42.50,
      "cost_ea": 12.80,
      "min_price_ea": 21.25,
      "quantity_12m": 8400.0,
      "prod_icc_code": "ICC-2210",
      "prod_hierarchy": "WC0301",
      "uom": "EA",
      "proposed_revenue": 356000.0,
      "historic_revenue": 356000.0
    }
  ]
}
```

## Response schema

Static ML invoke response (body). Generated `x_id` is returned in the `X-Id` header and stored in SQLAlchemy with the request + response payloads.

```json
{
  "cohort_segment_key": " ",
  "pricing_reasoning": " ",
  "products": [
    {
      "prod_num": "1642201",
      "lower_corridor_ea": 0.0,
      "target_price_ea": 0.0,
      "upper_corridor_ea": 0.0,
      "segment_mid_point_ea": 0.0,
      "price_elasticity": 0.0
    }
  ]
}
```

## Model version

Configured in `.env` / `settings.toml`:

- `MLAPI_ML_MODEL_VERSION=v1.0.0`
- Dynaconf key: `ML_MODEL_VERSION`

Exposed on `GET /health` and stored on each `ml_transactions` row.

## Blob process

1. App startup event runs `MLModelManagerFromBlob.check_and_evaluate_ml_model()`.
2. That method reads `ml_model_version` from settings and calls `BlobDownload.download_blob(container, blob_name)`.
3. Blob download is a class-level hook only (`'''Implement your code'''`). No real Azure/S3 download yet.

Blob settings: `BLOB_ACCOUNT_URL`, `BLOB_CONTAINER_NAME`, `BLOB_MODEL_PATH`.

## SQL backend

Switch with `MLAPI_SQL_BACKEND`:

| Value | Engine |
| --- | --- |
| `sqlite` (default) | Local file `sqlite:///./ml_api.db` |
| `azure_sql` | Azure SQL Database via `mssql+pyodbc` |

Azure SQL (when `MLAPI_SQL_BACKEND=azure_sql`):

```
MLAPI_AZURE_SQL_SERVER=myserver.database.windows.net
MLAPI_AZURE_SQL_DATABASE=ml_api
MLAPI_AZURE_SQL_USERNAME=mluser
MLAPI_AZURE_SQL_PASSWORD=***
MLAPI_AZURE_SQL_DRIVER=ODBC Driver 18 for SQL Server
```

Or set `MLAPI_AZURE_SQL_CONNECTION_STRING` to a full SQLAlchemy URL. Install Microsoft ODBC Driver 18 and `pyodbc` before using Azure SQL.

## MCP (FastMCP)

`MCPInvoke.invoke_mcp` is a generic FastMCP client call. Details come from config:

- `MLAPI_MCP_ENDPOINT`
- `MLAPI_MCP_TRANSPORT`
- `MLAPI_MCP_SERVER_NAME`
- `MLAPI_MCP_TOOL_NAME`
- `MLAPI_MCP_TIMEOUT_SECONDS`

If `MLAPI_MCP_ENDPOINT` is empty, the call is skipped. With a tool name it runs `call_tool`; with `resource_uri` it runs `read_resource`; otherwise it lists tools.

## Azure Web App config

Application settings JSON is generated from `.env` into `azure_web_app/appsettings.json`:

```bash
python azure_web_app/generate_appsettings.py
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: `GET /health`
- ML invoke: `POST /api/v1/ml/invoke`

Postman collection and environment live in `postman/`. Implementation notes are in `IMPLEMENTATION.md`.
