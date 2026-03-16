run:
	uv run python -m uvicorn src.api.app:app --reload --port 8001

migrate:
	uv run python -m alembic upgrade head

migration:
	uv run python -m alembic revision --autogenerate -m "$(msg)"

test:
	uv run python -m pytest

lint:
	uv run ruff check src/
