## Why

The FastAPI backend is still missing the `sysVariable` module that the shared frontend expects for user-defined SQL and filter variables, and several `sysParameter` endpoints still return 404 or incomplete behavior. This blocks frontend parity for system configuration and dynamic query workflows.

## What Changes

- Add a new `sysVariable` backend module with definition CRUD, value CRUD, repository/service layers, and router registration.
- Add SQLAlchemy models and Pydantic schemas for variable definitions and variable values using existing FastAPI backend conventions.
- Fill in missing `sysParameter` endpoints for online map lookup variants and default/share/UI/login settings.
- Add route tests that verify endpoint registration, response wrapping, and auth enforcement for the new protected APIs.

## Capabilities

### New Capabilities
- `sys-variable-management`: Manage user-defined system variables and their selectable values for use in SQL queries and dataset filters.

### Modified Capabilities
- `backend-contract-compatibility`: Extend route/auth coverage so the migrated backend explicitly serves the frontend `sysVariable` and missing `sysParameter` contracts.

## Impact

- Affected backend code lives in `core/pydataease-backend/app/models/`, `app/schemas/`, `app/repositories/`, `app/services/`, `app/routers/`, and `tests/`.
- Adds new `/sysVariable/**` API endpoints and completes missing `/sysParameter/**` endpoints expected by the shared frontend.
- No Alembic migration is included in this slice; table generation is deferred to later autogeneration work.
- Verification for implementation should cover L0 backend (`uv run ruff check .`) plus targeted contract/auth route tests and app import validation; broader L1 regression remains recommended because the change touches routers, services, and repositories.
