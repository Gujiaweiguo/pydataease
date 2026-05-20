## Why

The Python backend already enforces menu and resource permissions, but the shared frontend still calls Java-era `/auth/*` APIs to read and save permission assignments. Without these endpoints, administrators cannot configure menu or business-resource permissions through the UI, so the Java backend remains a functional fallback for permission management.

## What Changes

- Add FastAPI-compatible authorization management endpoints required by `core/core-frontend/src/api/auth.ts`:
  - `GET /de2api/auth/busiResource/{flag}`
  - `GET /de2api/auth/menuResource`
  - `POST /de2api/auth/busiPermission`
  - `POST /de2api/auth/menuPermission`
  - `POST /de2api/auth/saveBusiPer`
  - `POST /de2api/auth/saveMenuPer`
  - `POST /de2api/auth/busiTargetPermission`
  - `POST /de2api/auth/menuTargetPermission`
  - `POST /de2api/auth/saveBusiTargetPer`
  - `POST /de2api/auth/saveMenuTargetPer`
- Add the frontend helper endpoint `GET /de2api/user/org/option` for selecting users while configuring authorization.
- Reuse the existing permission catalog and grant tables instead of introducing a parallel permission model.
- Preserve existing permission enforcement behavior: this change exposes configuration APIs and must not weaken authentication, menu filtering, or resource checks.
- Add contract and authorization tests for the new endpoints using the existing FastAPI response wrapper and `X-DE-TOKEN` auth conventions.

## Capabilities

### New Capabilities
- `auth-permission-frontend-contract`: Provides the frontend-compatible authorization management API contract for menu resources, business resources, role/user/org grants, target permission lookup, and permission saving.

### Modified Capabilities
- `backend-contract-compatibility`: New `/auth/*` and `/user/org/option` endpoints become migrated backend contract endpoints and must be covered by route/auth/response-wrapper tests instead of being skipped as unimplemented.

## Impact

- Affects the active Python/FastAPI backend in `core/pydataease-backend/`.
- Expected backend additions include a new auth-permission router/service/schema layer and repository methods over existing permission models.
- Expected existing-code reuse includes `PermissionService`, menu/resource catalog data, `CorePermissionPoint`, `CoreRolePermission`, `CoreUserPermission`, and `CoreOrgPermission`.
- Frontend code should not require structural changes because this change targets the existing paths used by `core/core-frontend/src/api/auth.ts`.
- Required gates: **L0 backend** (`uv run ruff check .`) and **L1 backend** (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`) because this is API/auth/repository work. If implementation adds or changes tables, **L2 backend** (`uv run alembic upgrade head`) is also required.
- No Docker, packaging, or release-user-journey validation is required for the proposal itself; release validation can inherit normal backend gates when implementation begins.
