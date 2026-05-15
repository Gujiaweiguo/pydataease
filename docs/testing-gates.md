# Testing Gates

This project uses layered testing gates based on the repository's current capabilities. The goal is to cover the highest-risk changes without forcing every contributor to run every expensive check on every change.

## Change types and required commands

### 1. Docs / comments / OpenSpec only
- Required checks: typo / spell checks only
- Hard gate: typo checks must pass
- Soft gate: none

### 2. Backend internal logic
Run from `core/pydataease-backend/`:
- `uv run ruff check .`
- `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`

Hard gate:
- lint passes
- non-e2e backend tests pass

### 3. API / auth / repository changes
Run from `core/pydataease-backend/`:
- `uv run ruff check .`
- `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`

Hard gate:
- lint passes
- non-e2e backend tests pass

Soft gate:
- missing contract/auth/route coverage should be called out during verify

### 4. Database / integration / external service changes
Run from `core/pydataease-backend/`:
- `uv run ruff check .`
- `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- `uv run alembic upgrade head`

Hard gate:
- backend lint passes
- non-e2e backend tests pass
- migrations apply cleanly

Soft gate:
- real e2e is recommended when runnable infrastructure is available

### 5. Frontend / UI changes
Run from `core/core-frontend/`:
- `npm run ts:check`
- `npm run lint`
- `npm run lint:stylelint`

When routing, packaging outputs, or static assets are affected, also run:
- `npm run build:distributed`

Hard gate:
- TypeScript, ESLint, and stylelint pass
- distributed build passes when packaging outputs are affected

### 6. Release / packaging sensitive changes
Use the affected subsystem gates above, then add final release validation:
- Python backend: backend Docker build
- Frontend packaging: `npm run build:distributed`
- Desktop packaging: `mvn clean install` then `cd core && mvn clean package -Pdesktop -U -Dmaven.test.skip=true`
- High-risk user journey changes: `uv run pytest tests/test_e2e_creation_flow.py -v` when a runnable environment exists

## OpenSpec responsibility split

### verify
- classifies the change type from the implementation surface
- selects the minimum required gates
- records required commands, hard failures, and soft warnings

### archive
- inherits verify's hard-gate result
- must not archive changes whose required gates are still failing
- may proceed with user confirmation when only warnings remain

### release
- acts as the final hard gate
- validates build, package, and runnable user-journey checks for the affected release surface

## Why real e2e is not a default PR gate

The repository currently has one real backend e2e test, `tests/test_e2e_creation_flow.py`, and it depends on a runnable environment at `localhost:8100`. Because that is not a cheap or always-available CI precondition, the default PR gate excludes it. Use it for release-grade validation or explicitly high-risk changes.
