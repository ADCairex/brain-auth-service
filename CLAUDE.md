# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

**brain-auth-service** is the authentication microservice for the brain-app platform. It handles user registration, login, token issuance, and session management. It runs on port **8001** and is called exclusively through the **api-gateway** (never directly from the frontend in production).

## Commands

```bash
uv sync                                                               # Install dependencies
uv run python -m uvicorn src.api.app:app --reload --port 8001        # Start dev server
uv run python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8001  # Production start

make run                              # Alias for dev server
make migrate                          # Apply pending Alembic migrations
make migration msg="describe change"  # Generate new migration
make test                             # Run tests
make lint                             # Lint with ruff
```

Environment: copy `.env.example` to `.env` and fill in all variables (especially `SECRET_KEY`).

## Architecture

FastAPI + SQLAlchemy (sync) + PostgreSQL. Migrations via Alembic. Schema: `auth`.

```
src/api/
├── app.py           # FastAPI instance, CORS middleware, router registration, create_all
├── config.py        # pydantic-settings: all env vars from .env
├── database.py      # SQLAlchemy engine, SessionLocal, Base, get_db dependency
├── models.py        # ORM: User
├── schemas.py       # Pydantic I/O: RegisterRequest, LoginRequest, UserOut, OkResponse
└── endpoints/
    └── auth.py      # /auth — register, login, refresh, logout, me
```

```
alembic/             # Migration env and versions
alembic.ini          # Alembic configuration
```

## Database

- PostgreSQL, database `brain`, schema `auth`
- Connection string uses `options=-csearch_path%3Dauth` to set the search path
- Single table: `users` (id, email, hashed_password, created_at)

Create the schema before running migrations:
```sql
CREATE SCHEMA IF NOT EXISTS auth;
```

Then: `make migrate`

## Key patterns

- **DB session**: injected via `Depends(get_db)` in every endpoint.
- **Password hashing**: bcrypt via the `bcrypt` library. Never store plain text.
- **Tokens**: PyJWT, algorithm HS256. `SECRET_KEY` from environment only — never hardcoded.
- **Cookies**: all tokens set as `httpOnly` cookies. Never returned in response body.
  - `access_token`: 15 minutes, `samesite=lax`, `secure=True` outside development.
  - `refresh_token`: 7 days, same flags.
- **JWT payload** (access): `{"sub": str(user.id), "email": user.email, "exp": ...}`
- **JWT payload** (refresh): `{"sub": str(user.id), "exp": ...}`

## API surface

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create user → 201, `{ ok: true }` |
| POST | `/auth/login` | Validate credentials, set httpOnly cookies → `{ ok: true }` |
| POST | `/auth/refresh` | Issue new access_token from refresh_token cookie → `{ ok: true }` |
| POST | `/auth/logout` | Clear both cookies → `{ ok: true }` |
| GET | `/auth/me` | Return `{ id, email }` from access_token cookie |

## Data models

| Model | Table | Key fields |
|-------|-------|------------|
| `User` | `users` | `id`, `email`, `hashed_password`, `created_at` |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string with `search_path=auth` |
| `SECRET_KEY` | — | JWT signing secret — must match api-gateway's `SECRET_KEY` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token lifetime |
| `ENVIRONMENT` | development | `development` disables `secure` flag on cookies |

## What NOT to do

- Do not add business logic here. This service only handles auth.
- Do not return tokens in response body — httpOnly cookies only.
- Do not expose any user field beyond `id` and `email`.
- Do not expose this service via Traefik directly — only api-gateway calls it.
- Do not change the JWT payload structure without updating api-gateway.
