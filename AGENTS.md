# AGENTS.md

## Repo shape that matters
- The repo has two backends: an **Active Python/FastAPI backend** and a **Legacy Java/Spring Boot backend**, plus a shared frontend.
- `de-xpack/` is a git submodule boundary. Treat it as external unless the submodule contents are present and the task explicitly requires it.

## Active backend: Python/FastAPI (`core/pydataease-backend/`)

**Entrypoint**: `core/pydataease-backend/app/main.py`
**Config**: `core/pydataease-backend/app/settings/config.py` + `.env`
**Env selector**: `DE_ENV=dev|prod`

### Commands (run from `core/pydataease-backend/`)
- `uv sync` — install dependencies
- `uv run pytest tests/ -v` — run tests (84 implementation tests)
- `uv run python -c "from app.main import app; print(app.title)"` — verify import
- `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000` — run dev server
- `uv run alembic upgrade head` — run database migrations

### Architecture
4-layer pattern: Routers → Services → Repositories → Models
- Schemas use Pydantic v2 with camelCase compatibility via AliasChoices
- Middleware stack: auth (X-DE-TOKEN), whitelist, response wrapper (ResultMessage)
- Tasks: APScheduler with async export worker

### Database
- PostgreSQL 16 with SQLAlchemy 2.x async + Alembic migrations
- Models use BigInteger IDs (`time.time_ns()`), JSONB, no autoincrement
- Migrations live in `core/pydataease-backend/alembic/versions/`

### API contract
- Prefix: `/de2api` (mounted by api_router in main.py)
- Response wrapper: `{"code": 0, "data": ..., "msg": ""}` (ResultMessage middleware)
- Auth headers: `X-DE-TOKEN`, `X-DE-LINK-TOKEN`, `X-EMBEDDED-TOKEN`
- WebSocket at `/websocket` (compatibility stub)

### Key env vars (DE_ prefix)
- `DE_ENV=dev|prod`
- `DE_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname`
- `DE_SECRET_KEY=...`
- `DE_SHARE_SECRET_KEY=...`

### Deployment
- Dev: local FastAPI + Docker PostgreSQL (`docker-compose.dev.yml`)
- Prod: Docker `pydataease-app` + `pydataease-pg` (`docker-compose.prod.yml`)
- Internal port 8000, external 8100
- Dockerfile: multi-stage uv build
- Entrypoint: `scripts/entrypoint.sh` (alembic + uvicorn)
- Health check: `scripts/healthcheck.py` → GET `/health`

## Legacy backend: Java/Spring Boot (`core/core-backend/`)

**Entrypoint**: `core/core-backend/src/main/java/io/dataease/CoreApplication.java`
**Config**: `core/core-backend/src/main/resources/application.yml`
**Build**: `core/pom.xml` owns `core-backend` and `core-frontend` modules

### Build and packaging traps
- `mvn clean install` at repo root does **not** build the main `core` app; it builds the root reactor (only `sdk`).
- Frontend build logic is duplicated across npm and Maven:
  - frontend scripts live in `core/core-frontend/package.json`
  - `core/core-frontend/pom.xml` vendors Node `v23.11.0` and npm `10.9.2`, runs `npm install`, then `npm run build:distributed`
- Desktop CI/build flow: see `.github/workflows/desktop_build.yml`
- Backend packaging expects frontend assets in `core/core-frontend/dist`; Maven copies them into `core/core-backend/src/main/resources/static`.

### Backend data and profiles
- Flyway migrations are profile-specific:
  - server: `core/core-backend/src/main/resources/db/migration`
  - desktop: `core/core-backend/src/main/resources/db/desktop`
- Default port: `8100` (`application.yml`)
- `standalone` uses MySQL, `desktop` uses H2, `distributed` disables Flyway

### Deployment
- `Dockerfile` expects the built jar at `core/core-backend/target/CoreApplication.jar`
- `installer/dectl` is the operational control script for compose-based installs

## Frontend (`core/core-frontend/`) — unchanged
- Run from `core/core-frontend/`:
  - `npm run dev` / `npm run ts:check` / `npm run lint` / `npm run lint:stylelint`
  - `npm run build:base` / `npm run build:distributed`
- Formatting: `core/core-frontend/.editorconfig` (2 spaces, LF, UTF-8)

## CI and contribution signals
- PRs satisfy `.github/PULL_REQUEST_TEMPLATE.md`: passing tests, coverage, Conventional Commit messages, docs impact review.
- Typo checking via `.typos.toml`; `mapFiles/**` and `docs` are excluded.
- Automated PR review in `.github/workflows/llm-code-review.yml` targets code files and answers in Chinese.
