## Context

The FastAPI backend rewrite is feature-complete with 160 unit/contract tests passing against `httpx.AsyncClient(ASGITransport)`. The Vue frontend has never connected to this new backend. The frontend dev server (Vite, port 8080) proxies `/api/*` to `http://localhost:8100/de2api/*`. The backend currently runs on port 8000 via uvicorn. We need to verify the full stack works: PostgreSQL → FastAPI → Vite proxy → Vue frontend.

**Current state:**
- Frontend proxy config: `core/core-frontend/config/dev.ts` — proxy `/api` → `http://localhost:8100/de2api`
- Frontend env: `VITE_API_BASEPATH=/api` (dev mode)
- Frontend login: `POST /api/login/localLogin` with RSA-encrypted credentials
- Frontend auth header: `X-DE-TOKEN` with JWT
- Backend auth endpoints: `GET /de2api/dekey`, `POST /de2api/login/localLogin`, `GET /de2api/login/refresh`, `GET /de2api/logout`
- Backend response wrapper: `ResultMessage` middleware wraps `/de2api/*` responses as `{"code": 0, "data": ..., "msg": ""}`
- Default admin: `admin` / `DataEase@123456`

## Goals / Non-Goals

**Goals:**
- Verify frontend dev server can connect to FastAPI backend through Vite proxy
- Validate login auth flow end-to-end (RSA key fetch → encrypted login → JWT → protected endpoint → refresh → logout)
- Confirm API path routing works: `/api/*` → proxy → `http://localhost:8100/de2api/*`
- Verify `ResultMessage` response format matches frontend axios interceptor expectations
- Create reproducible E2E test suite for ongoing regression

**Non-Goals:**
- Full UI visual testing (screenshot diff, CSS validation)
- Testing unimplemented endpoints (17 skipped contract tests)
- Performance benchmarking
- Production Docker deployment testing
- Frontend code modifications

## Decisions

### D1: Playwright for E2E tests
**Decision:** Use Playwright to drive the Vue frontend browser and verify end-to-end flows.
**Rationale:** Playwright supports real browser automation, can verify SPA routing, and has excellent async/await support. The `/playwright` skill is available.
**Alternative:** Raw `httpx` calls to backend only — rejected because it skips the Vite proxy layer which is the critical integration point.

### D2: FastAPI on port 8100 for dev
**Decision:** Run `uvicorn app.main:app --host 0.0.0.0 --port 8100` in dev mode to match the Vite proxy target.
**Rationale:** Frontend proxy config points to `localhost:8100`. Changing it would require frontend modifications (non-goal). Port 8100 also matches the Java backend's default port, easing future migration.
**Alternative:** Run on 8000 and change frontend proxy config — rejected per non-goal of no frontend code changes.

### D3: Docker PostgreSQL for dev environment
**Decision:** Use `docker run postgres:16` with mapped port 5432 for development database.
**Rationale:** Matches the production PostgreSQL requirement. `docker-compose.dev.yml` already specifies this setup. Simple, reproducible.
**Alternative:** Use the already-running MySQL container — rejected because the target is PostgreSQL.

### D4: Separate E2E test directory
**Decision:** Place E2E tests in `core/pydataease-backend/tests/e2e/` with `conftest.py` that manages server lifecycle.
**Rationale:** Separates integration tests from unit/contract tests. Can be run independently with `pytest tests/e2e/ -v`. Has its own fixtures for real HTTP (not ASGI transport).

### D5: Admin user seeding via Alembic migration
**Decision:** Run `alembic upgrade head` (which includes user table migration) then seed admin user programmatically via a setup script or test fixture.
**Rationale:** The user table migration already exists. Seeding needs to happen once before E2E tests run.

## Risks / Trade-offs

- **[RSA key mismatch]** Frontend encrypts with the public key from `/dekey`, backend decrypts with private key → Mitigation: Ensure `DE_RSA_PRIVATE_KEY_PATH` env var points to a valid key pair; test fixture generates a test key pair
- **[Port conflict]** Port 8100 may be in use → Mitigation: Check availability before starting; provide override via env var
- **[PostgreSQL not available]** E2E tests need a running database → Mitigation: Docker setup script; skip E2E tests if DB unavailable (with clear error)
- **[Node.js dependency install time]** Frontend `npm install` can be slow → Mitigation: Use `npm ci` with lockfile; cache node_modules
- **[Response format mismatch]** Frontend may expect specific field names → Mitigation: camelCase `serialization_alias` already configured; E2E test will catch any mismatch
