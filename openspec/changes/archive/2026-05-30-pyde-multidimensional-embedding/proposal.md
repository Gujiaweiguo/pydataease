## Plan Reference

- **PLAN_ID**: `pydataease-dataease-capabilities-plan-v1`
- **Execution order**: 4th of 6 (plan labels it "Change 5" but it executes before Change 4)
- **Prerequisites**: `pyde-admin-config-foundation` (Change 1), `pyde-system-variables-parameter-contract` (Change 3)
- **Subsequent**: `pyde-identification-platform-integration` (Change 4)
- **Rationale for ordering**: The embedding contract must be stable before external identity is added in Change 4. Token and parameter semantics for share/embed are shared infrastructure that identification settings depend on.

## Why

The share/embed/token/outerParams infrastructure already exists in pydataease, but the runtime context is fragmented across separate code paths with inconsistent parameter semantics. There is no unified model for how `X-DE-LINK-TOKEN`, `X-EMBEDDED-TOKEN`, share tokens, outer params, jump params, and resource-type contexts relate to each other. This fragmentation blocks a coherent embedding admin experience and makes it impossible to add new resource types (like data filing embeds) without duplicating token and parameter logic.

## What Changes

- Unify the runtime context model for share, link, and embed access into a single coherent contract that covers token header responsibility boundaries, fallback rules, and error scenarios.
- Define a multidimensional embedding control plane that covers Dashboard, Chart, DataV, and Data Filing (reserved) resource types with admin-facing configuration for resource-level switches, domain policies, password/ticket/expiry rules, embed parameter injection, and link jump routing.
- Enforce that no second authentication header or embed protocol is introduced. All embed access extends the existing `X-DE-TOKEN` / `X-DE-LINK-TOKEN` / `X-EMBEDDED-TOKEN` chain.
- Connect the canonical parameter resolution contract (from Change 3) to the embed/share runtime, ensuring outer params, jump params, busiFlag, resource type, and share expiry are resolved through a single precedence chain.

## Capabilities

### New Capabilities
- `embedding-control-plane`: Admin-facing configuration and runtime enforcement for multidimensional embedding across multiple resource types (Dashboard, Chart, DataV, Data Filing reserved). Covers resource-level embed switches, domain policies, password/ticket/expiry rules, parameter injection, link jump routing, and unified error handling.

### Modified Capabilities
- `backend-contract-compatibility`: Extend the share/embed token handling and parameter injection paths to use the unified runtime context model and canonical parameter resolution contract.

## Impact

- Affects `core/pydataease-backend/app/middleware/auth.py` (token path unification), `app/routers/share.py` (embed token management), `app/routers/outer_params.py` (parameter injection), and `app/routers/link_jump.py` (jump routing).
- Frontend embed store at `core/core-frontend/src/store/modules/embedded.ts` may need contract alignment.
- Adds admin API surface for embed configuration per resource type.
- No new Alembic migration is expected in the initial planning artifact; model changes are deferred to implementation.
- Verification gates: L0 (`uv run ruff check .`) + L1 (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`). Frontend L0 gates apply only if admin UI pages are touched.

## Non-goals

- Will not introduce a second authentication header or embed protocol. All embed access extends existing token headers.
- Will not implement full platform identity federation. That belongs to Change 4 (`pyde-identification-platform-integration`).
- Will not let data filing write-path become an embed prerequisite. Data filing embed is reserved as a future resource type slot.
- Will not mix platform integration concerns into this change.
- Will not bypass existing `AuthMiddleware` for any embed or share path.

## Gate Layer

- **L0**: `cd core/pydataease-backend && uv run ruff check .` (mandatory)
- **L0 Frontend**: `cd core/core-frontend && npm run ts:check && npm run lint` (only when admin UI is touched)
- **L1**: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` (mandatory for API/auth/repository changes)
- **L1 Import**: `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"` (mandatory)
