#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Starting ML API at http://${HOST}:${PORT}"
echo "Swagger: http://${HOST}:${PORT}/docs"
exec uvicorn app.main:app --reload --host "${HOST}" --port "${PORT}"
