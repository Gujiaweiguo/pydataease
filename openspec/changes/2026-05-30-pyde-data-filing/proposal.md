## Plan Reference

- **PLAN_ID**: `pydataease-dataease-capabilities-plan-v1`
- **Execution order**: 6th of 6 (final change in the program)
- **Prerequisites**: `pyde-admin-config-foundation` (Change 1), `pyde-system-variables-parameter-contract` (Change 3), `pyde-multidimensional-embedding` (Change 5), `pyde-identification-platform-integration` (Change 4)
- **Subsequent**: none (final change)
- **Risk level**: HIGH. Data filing is a write-path capability that requires ACL, audit, idempotency, and failure recovery by design. It cannot be treated as a simple datasource switch.

## Why

Data filing is a write-path capability that lets users submit data back to configured datasources through form-based interfaces. The existing `enable_data_fill` flag on engine and datasource models is only a switch, not a complete capability. There is no domain model for form configurations, submission records, audit trails, field validation, permission separation, failure recovery, or idempotency guarantees. Opening a write path without these safeguards would allow uncontrolled data mutation in connected datasources, which is unacceptable for any production deployment.

This change takes a "admin-first, write-path safety-first" approach: the backend model, ACL, audit, and failure-recovery boundaries are defined before any user-facing submission workflow is built.

## What Changes

- Define the data filing domain model: form/filing configuration, published state, submission records, status records, audit records, error codes, and idempotency strategy.
- Establish that `enable_data_fill` is a capability flag only, not a complete implementation. Supplement it with datasource/engine write-back constraints, field validation, permission layering, and failure recovery boundaries.
- Define the minimum viable filing workflow priority: admin configuration, publish, submit, query, audit.
- Define admin workflow capabilities: create, publish, disable, permission assignment, record viewing, and exception retry/replay.
- Define failure scenarios and handling: field validation failure, target datasource not writable, permission denied, duplicate submission, partial write failure.
- Prohibit anonymous public writes. All submissions require authenticated access with appropriate ACL checks.
- Define dependencies on system variables (for parameterized forms), embedding context (for embedded filing forms), and authentication settings (for submitter identity).

## Capabilities

### New Capabilities
- `data-filing-write-path`: A write-path capability for submitting data to configured datasources through form-based interfaces, with built-in ACL, audit trail, idempotency guarantees, field validation, failure recovery, and admin lifecycle management (create, publish, disable, permission assignment, record viewing, retry).

### Modified Capabilities
- `backend-contract-compatibility`: Extend engine and datasource models to support data filing write-path constraints beyond the existing `enable_data_fill` flag.

## Impact

- Affects `core/pydataease-backend/app/models/engine.py` (`enable_data_fill` context), `app/models/datasource.py` (datasource write constraints), and adds new models for filing configuration, submission, audit, and status tracking.
- Affects `app/routers/share.py` and `app/middleware/auth.py` for embed-context filing form access boundaries.
- Adds new admin API surface for filing configuration, lifecycle management, submission handling, and audit queries.
- Frontend `embedded.ts` store has a reserved `dfId` field indicating the expected embed-side contract.
- Verification gates: L0 (`uv run ruff check .`) + L1 (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`). Frontend L0 gates apply if admin UI is touched.
- Rollback: close data-filing flag, stop accepting new submissions, retain all existing records and audit data. No destructive rollback permitted.

## Non-goals

- Will not expand the first release into a complex drag-and-drop low-code form designer. The minimum viable workflow is admin configuration, publish, submit, query, audit.
- Will not allow bypassing ACL to write directly to datasource. All writes go through the filing pipeline with permission checks.
- Will not allow anonymous public writes. All submissions require authenticated access.
- Will not treat data filing as a simple datasource/engine switch. The `enable_data_fill` flag is a gate, not the implementation.
- Will not perform destructive rollback. When the data-filing flag is disabled, existing submission records and audit trails are preserved.

## Gate Layer

- **L0**: `cd core/pydataease-backend && uv run ruff check .` (mandatory)
- **L0 Frontend**: `cd core/core-frontend && npm run ts:check && npm run lint` (only when admin UI is touched)
- **L1**: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` (mandatory for write-path changes)
- **L1 Import**: `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"` (mandatory)
