param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$Activate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $Activate) {
    . $Activate
} else {
    throw "Virtualenv activate script not found: $Activate"
}

if ((-not (Test-Path ".env")) -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Starting ML API at http://${HostAddress}:${Port}"
Write-Host "Swagger: http://${HostAddress}:${Port}/docs"
uvicorn app.main:app --reload --host $HostAddress --port $Port
