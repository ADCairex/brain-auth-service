#!/bin/sh
set -e

echo "Running migrations..."
uv run alembic upgrade head

echo "Starting server..."
exec uv run python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8001
