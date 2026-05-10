## Why

The FastAPI backend rewrite (T01-T13), deferral resolution (D1-D5), and login auth flow (L1-L9) are complete with 160 passing tests — but all verification has been unit/contract-level against `httpx.AsyncClient`. The Vue frontend has never connected to the new backend. Before building more endpoints, we need end-to-end confirmation that the frontend dev server can reach the FastAPI backend through the Vite proxy and complete the login → dashboard flow. This is the critical integration gate: if the proxy path mapping, RSA encryption handshake, JWT token lifecycle, or response wrapper format is off, all downstream work is built on sand.

## What Changes

- **Dev environment bootstrap**: `docker-compose.dev.yml` for PostgreSQL, FastAPI on port 8100 (matching frontend Vite proxy target), Vue dev server on port 8080
- **Integration test suite**: Playwright-based E2E tests covering login flow (RSA key fetch → encrypted password → JWT response → auth header propagation)
- **API path alignment verification**: Confirm frontend `/api/*` → Vite proxy → `http://localhost:8100/de2api/*` routing works for all implemented endpoints
- **Response format validation**: Verify `ResultMessage` wrapper (`{"code": 0, "data": ..., "msg": ""}`) matches frontend axios interceptor expectations
- **Auth lifecycle test**: Full cycle — get RSA public key → encrypt password → login → receive JWT → access protected endpoint → refresh token → logout

## Capabilities

### New Capabilities
- `frontend-backend-integration`: End-to-end integration between Vue frontend and FastAPI backend via Vite dev proxy, covering dev environment setup, API path routing, and auth flow validation

### Modified Capabilities
- `login-auth-endpoints`: Verify existing spec requirements hold under real frontend consumption (RSA encryption handshake, JWT propagation)
- `backend-contract-compatibility`: Validate that ResultMessage response format and camelCase serialization work with frontend axios interceptors

## Impact

- **Dev infrastructure**: New `docker-compose.dev.yml` for PostgreSQL; FastAPI startup on port 8100; environment variables for dev mode
- **Testing**: New Playwright E2E test suite under `core/pydataease-backend/tests/e2e/`
- **Configuration**: FastAPI may need CORS headers or proxy trust headers for dev mode
- **Frontend**: No code changes — using existing Vue dev server with existing proxy config (`core/core-frontend/config/dev.ts`)
- **Dependencies**: `playwright` added as dev dependency
