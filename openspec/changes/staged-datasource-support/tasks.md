## 1. Datasource Contract and Dependency Setup

- [x] 1.1 Confirm the first-wave datasource API surface and request/response contract for PostgreSQL and MySQL only.
- [x] 1.2 Add any required MySQL driver/runtime dependencies and document whether Excel/CSV is included or deferred for this change.
- [x] 1.3 Define the shared datasource configuration model used for create connection, test connection, metadata browse, and query preview.

## 2. Backend Datasource Connectivity

- [x] 2.1 Implement PostgreSQL datasource create/test connection flow using the shared datasource contract.
- [x] 2.2 Implement MySQL datasource create/test connection flow using the shared datasource contract.
- [x] 2.3 Add explicit failure handling for invalid host, port, credentials, and unsupported deferred datasource types.

## 3. Metadata Introspection

- [x] 3.1 Implement PostgreSQL metadata introspection for databases/schemas/tables/columns as required by the frontend flow.
- [x] 3.2 Implement MySQL metadata introspection for databases/tables/columns as required by the frontend flow.
- [x] 3.3 Normalize metadata responses so the frontend can use one generic SQL datasource browsing flow.

## 4. Datasource-Aware Query Preview

- [x] 4.1 Extend the SQL execution engine so preview requests target the selected configured datasource instead of the internal runtime database.
- [x] 4.2 Preserve existing read-only guards for preview SQL, including SELECT/WITH-only enforcement and dangerous keyword rejection.
- [x] 4.3 Return explicit errors when preview requests reference missing, invalid, or unsupported datasource definitions.

## 5. Dataset and Frontend Integration

- [x] 5.1 Wire supported datasource metadata and preview APIs into dataset authoring flows in the FastAPI backend.
- [x] 5.2 Update the frontend datasource and dataset flow to expose only PostgreSQL/MySQL in the first wave and keep deferred datasource types out of the MVP path.
- [x] 5.3 Verify that datasets authored from supported datasources can be consumed by existing chart and dashboard flows.

## 6. Verification

- [x] 6.1 Run fast backend checks: `cd core/pydataease-backend && uv run ruff check .`
- [x] 6.2 Run default backend tests: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] 6.3 Run frontend checks if frontend datasource flows change: `cd core/core-frontend && npm run ts:check && npm run lint && npm run lint:stylelint`
- [x] 6.4 Run integration-sensitive backend checks for datasource/runtime changes: `cd core/pydataease-backend && uv run alembic upgrade head`
- [ ] 6.5 Run release-only packaging validation if new drivers or container setup change: `cd core/pydataease-backend && docker build -t pydataease-backend:ci .`
- [ ] 6.6 Run release-only user-journey validation in a runnable environment when preparing rollout: `cd core/pydataease-backend && uv run pytest tests/test_e2e_creation_flow.py -v`
