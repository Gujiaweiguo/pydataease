## 1. Dev Environment Bootstrap

- [x] 1.1 Start PostgreSQL 16 in Docker on port 5432 with a `pydataease` database and configure `DE_DATABASE_URL` env var
- [x] 1.2 Run `alembic upgrade head` to apply all migrations including the `core_user` table
- [x] 1.3 Seed the default admin user (username "admin", bcrypt-hashed "DataEase@123456") into the database
- [x] 1.4 Start FastAPI backend on port 8100 (`uvicorn app.main:app --host 0.0.0.0 --port 8100`) and verify `/health` returns 200
- [x] 1.5 Install frontend dependencies (`npm install` in `core/core-frontend/`) and start Vue dev server on port 8080 (`npm run dev`)

## 2. API Path Alignment Verification

- [x] 2.1 Verify `GET /api/dekey` through Vite proxy returns RSA public key (proxied to `http://localhost:8100/de2api/dekey`)
- [x] 2.2 Verify `POST /api/login/localLogin` through Vite proxy accepts RSA-encrypted credentials and returns JWT
- [x] 2.3 Verify `GET /api/login/refresh` through Vite proxy accepts current JWT and returns new token
- [x] 2.4 Verify `GET /api/logout` through Vite proxy returns success response
- [x] 2.5 Verify ResultMessage response format (`{"code": 0, "data": ..., "msg": ""}`) matches frontend axios interceptor expectations

## 3. E2E Test Suite

- [x] 3.1 Create `core/pydataease-backend/tests/e2e/` directory with `conftest.py` that manages server lifecycle (PostgreSQL, FastAPI, frontend)
- [x] 3.2 Add `playwright` as dev dependency in `pyproject.toml`
- [x] 3.3 Implement E2E test: login page loads and fetches RSA public key successfully
- [x] 3.4 Implement E2E test: admin user logs in with encrypted credentials and receives JWT
- [x] 3.5 Implement E2E test: authenticated user accesses a protected endpoint and gets valid data
- [x] 3.6 Implement E2E test: token refresh returns new valid JWT
- [x] 3.7 Implement E2E test: logout completes successfully
- [x] 3.8 Run full E2E test suite and verify all tests pass

## 4. Final Verification

- [x] 4.1 Verify all existing unit/contract tests still pass (160 passed, 17 skipped)
- [x] 4.2 Verify E2E tests pass against live stack
- [x] 4.3 Verify no regressions in build (`uv sync` + `uv run pytest tests/ -v`)

## 5. Additional Fixes (discovered during integration)

- [x] 5.1 Fix admin password bcrypt hash in Alembic migration (original hash didn't match "DataEase@123456")
- [x] 5.2 Add frontend bootstrap stub endpoints (xpackModel, model, i18nOptions, defaultSettings, ui, auth status)
- [x] 5.3 Fix dekey endpoint to return Java-compatible AES-encrypted format (not raw PEM)
- [x] 5.4 Fix RSA padding from OAEP to PKCS1v15 (matching JSEncrypt/Java behavior)
- [x] 5.5 Add `/user/info` endpoint for post-login user store population
