# AGENTS.md

## Repo shape that matters
- The repo has a **Python/FastAPI backend** and a shared frontend.
- `de-xpack/` is a git submodule boundary. Treat it as external unless the submodule contents are present and the task explicitly requires it.

## Active backend: Python/FastAPI (`core/pydataease-backend/`)

**Entrypoint**: `core/pydataease-backend/app/main.py`
**Config**: `core/pydataease-backend/app/settings/config.py` + `.env`
**Env selector**: `DE_ENV=dev|prod`

### Commands (run from `core/pydataease-backend/`)
- `uv sync` — install dependencies
- `uv run ruff check .` — fast backend lint gate
- `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — default backend gate for CI and verify
- `uv run pytest tests/test_e2e_creation_flow.py -v` — real user-journey e2e when a runnable environment exists
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

## Frontend (`core/core-frontend/`) — unchanged
- Run from `core/core-frontend/`:
  - `npm run dev` / `npm run ts:check` / `npm run lint` / `npm run lint:stylelint`
  - `npm run build:base` / `npm run build:distributed`
- Formatting: `core/core-frontend/.editorconfig` (2 spaces, LF, UTF-8)

## Layered testing gates

- **Docs / comments only**: typo/spell checks only; do not force full builds or backend suites.
- **Backend internal logic**: `uv run ruff check .` + `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- **API / auth / repository changes**: same backend gate, with extra attention to contract/auth/route coverage.
- **Database / integration / external service changes**: backend gate plus `uv run alembic upgrade head`. Defer backend Docker build to release-sensitive verification.
- **Frontend / UI changes**: `npm run ts:check` + `npm run lint` + `npm run lint:stylelint`; add `npm run build:distributed` when routing/assets/packaging outputs are affected.
- **Release / packaging changes**: inherit affected subsystem gates, then require final build/package validation.
- **OpenSpec responsibility split**:
  - `verify` selects required gates by change type and records hard failures vs soft warnings.
  - `archive` inherits verify hard-gate results and must block on failed required gates.
  - `release` is the final hard gate for build/package/user-journey validation.
- Keep real e2e out of default PR blocking unless the user explicitly asks for release-grade verification.

## Local dev environment (Docker containers)

Two shared containers are used for development. **Always use these, never create new ones.**

| Container | Image | Port | Purpose | Credentials |
|-----------|-------|------|---------|-------------|
| `postgres16` | `pgvector/pgvector:pg16` | 5432 | **内部元数据库** — FastAPI 后端的系统库（用户、角色、仪表板、数据源配置等） | `dataease:dataease` / db: `dataease` |
| `mysql8` | `mysql:8.0` | 3306 | **外部 MySQL 数据源** — 用于测试用户添加的 MySQL 类型数据源连接 | `root:` (空密码) / 或看容器 env |

- `.env` 中 `DE_DATABASE_URL=postgresql+asyncpg://dataease:dataease@127.0.0.1:5432/dataease`
- 如果容器没启动：`docker start postgres16 mysql8`

## CI and contribution signals
- PRs satisfy `.github/PULL_REQUEST_TEMPLATE.md`: passing tests, coverage, Conventional Commit messages, docs impact review.
- Typo checking via `.typos.toml`; `mapFiles/**` and `docs` are excluded.
- Automated PR review in `.github/workflows/llm-code-review.yml` targets code files and answers in Chinese.
