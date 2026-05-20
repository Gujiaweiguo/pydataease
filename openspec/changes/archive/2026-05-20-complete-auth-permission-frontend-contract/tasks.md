## 1. Contract and Schema Setup

- [x] 1.1 Define request and response schemas for menu resources, business resources, permission lookup, target permission lookup, permission save payloads, and user org options in `app/schemas/auth_permission.py`.
- [x] 1.2 Confirm whether existing permission models can represent all required grant payloads; document and implement any migration only if a required persisted field is missing.
- [x] 1.3 Add repository helpers for querying permission points and role/user/org grants without duplicating existing permission logic.

## 2. Authorization Management Service

- [x] 2.1 Implement `AuthPermissionService` for menu resource tree generation using existing menu and permission catalog data.
- [x] 2.2 Implement business resource tree/list generation for supported flags including dashboard, screen, dataset, and datasource.
- [x] 2.3 Implement menu and business permission lookup for supported target types.
- [x] 2.4 Implement atomic save behavior for menu and business permission assignments.
- [x] 2.5 Implement target-specific permission lookup and save behavior for menu and business resources.
- [x] 2.6 Ensure save operations require authorization-management permission and reject unauthorized users without modifying grants.

## 3. FastAPI Routes

- [x] 3.1 Add `app/routers/auth.py` and register it in `app/main.py` under the existing `/de2api` API router.
- [x] 3.2 Implement `GET /auth/menuResource` and `GET /auth/busiResource/{flag}`.
- [x] 3.3 Implement `POST /auth/busiPermission` and `POST /auth/menuPermission`.
- [x] 3.4 Implement `POST /auth/saveBusiPer` and `POST /auth/saveMenuPer`.
- [x] 3.5 Implement `POST /auth/busiTargetPermission` and `POST /auth/menuTargetPermission`.
- [x] 3.6 Implement `POST /auth/saveBusiTargetPer` and `POST /auth/saveMenuTargetPer`.
- [x] 3.7 Implement `GET /user/org/option` in the appropriate user/org router using current-organization context.

## 4. Compatibility and Regression Tests

- [x] 4.1 Add route contract tests proving all new endpoints are mounted under `/de2api` and return `ResultMessage`-wrapped responses for valid authenticated requests.
- [x] 4.2 Add auth failure tests proving protected endpoints reject missing and invalid `X-DE-TOKEN` headers.
- [x] 4.3 Add service/repository tests for permission tree generation and grant lookup.
- [x] 4.4 Add save-read tests proving `saveBusiPer`, `saveMenuPer`, `saveBusiTargetPer`, and `saveMenuTargetPer` persist grants atomically and subsequent lookup returns them.
- [x] 4.5 Add authorization tests proving non-admin or unauthorized users cannot save permission assignments.
- [x] 4.6 Update backend contract tests so these endpoints are executed as implemented tests rather than skipped as unimplemented.

## 5. Verification

- [x] 5.1 Run fast backend lint: `cd core/pydataease-backend && uv run ruff check .`.
- [x] 5.2 Run default backend tests: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`.
- [x] 5.3 If a migration is added, run migration verification: `cd core/pydataease-backend && uv run alembic upgrade head`.
- [x] 5.4 Run a focused API smoke check for `/de2api/auth/menuResource`, `/de2api/auth/busiResource/dataset`, and one save-read permission flow with an authenticated admin token.
- [x] 5.5 Confirm no frontend API path changes are required in `core/core-frontend/src/api/auth.ts`.
