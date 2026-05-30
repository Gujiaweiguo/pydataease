## Plan Reference

- **PLAN_ID**: `pydataease-dataease-capabilities-plan-v1`
- **Execution order**: 5th of 6 (plan labels it "Change 4" but it executes after Change 5 because embedding contract must be stable before external identity is added)
- **Prerequisites**: `pyde-admin-config-foundation` (Change 1), `pyde-system-variables-parameter-contract` (Change 3), `pyde-multidimensional-embedding` (Change 5)
- **Subsequent**: `pyde-data-filing` (Change 6)
- **Rationale for ordering**: Token and parameter semantics for share/embed must be finalized before external identity sources are layered on top. Identification settings depend on a stable embedding runtime context.

## Why

The `/setting/authentication/status` endpoint currently returns an empty array as a stub. There is no admin-facing model for configuring default login methods, managing identity providers, or defining how external authentication sources map to local users and organizations. As a result, the system cannot support any external identity integration (LDAP, OIDC, CAS) without ad-hoc workarounds that bypass the existing token infrastructure. This change builds the backbone for authentication configuration and platform identity integration on top of the already-stable embedding contract.

## What Changes

- Design the identification settings backend model: default login method configuration, enabled provider list, provider status query contract, admin configuration entry points, and failure fallback rules to local login.
- Define the responsibility boundary between local login and external providers, including organization mapping, user mapping, and provider disable/enable strategy.
- Define the `/setting/authentication/status` evolution from empty-array stub to a stable status interface that describes provider enable/disable states and default login selection.
- Build a provider registry as an abstraction layer (LDAP / OIDC / CAS unified contract), not a one-shot implementation of all vendors.
- Define platform integration adapter strategy: configuration persistence, enable/disable lifecycle, callback handling, declarative claim mapping, error fallback, and local account fallback.
- Ensure share/embed/token paths and existing session boundaries are not affected by provider enable/disable.

## Capabilities

### New Capabilities
- `identification-settings`: Admin-facing configuration for authentication methods, default login strategy, identity provider registry (LDAP/OIDC/CAS abstraction), provider status exposure, and safe fallback to local login when external providers are disabled or failing.
- `platform-integration`: Provider adapter contract and strategy for external identity sources, covering configuration persistence, callback handling, declarative claim mapping, error fallback, and local account linkage. Designed for extensibility without depending on `de-xpack/`.

### Modified Capabilities
- `backend-contract-compatibility`: Extend `/setting/authentication/status` from stub to stable status interface. Add provider registry routes and admin configuration endpoints.

## Impact

- Affects `core/pydataease-backend/app/routers/bootstrap.py` (authentication status endpoint), `app/routers/login.py` (local login/refresh preserved), `app/middleware/auth.py` (token decode semantics unchanged), and `app/middleware/whitelist.py` (SSO path whitelist).
- Adds new admin API surface for provider configuration, status, and lifecycle management.
- Frontend login API at `core/core-frontend/src/api/login.ts` may need contract alignment for platform login calls.
- No changes to existing `X-DE-TOKEN` / `X-DE-LINK-TOKEN` / `X-EMBEDDED-TOKEN` semantics.
- Verification gates: L0 (`uv run ruff check .`) + L1 (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`). Frontend L0 gates apply if login UI is touched.

## Non-goals

- Will not promise full parity for all third-party vendor experiences in a single change. The provider registry is an abstraction; individual provider implementations may follow incrementally.
- Will not change existing token header semantics or introduce a new session model.
- Will not break existing `/login/localLogin` or `/login/refresh` behavior.
- Will not extend into notification center, plugin marketplace, or ecosystem integration features.
- Will not break share/embed/runtime token paths.

## Gate Layer

- **L0**: `cd core/pydataease-backend && uv run ruff check .` (mandatory)
- **L0 Frontend**: `cd core/core-frontend && npm run ts:check && npm run lint` (only when login/admin UI is touched)
- **L1**: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` (mandatory for auth/route changes)
- **L1 Import**: `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"` (mandatory)
