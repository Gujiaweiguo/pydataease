## Plan Reference

- PLAN_ID = `pydataease-dataease-capabilities-plan-v1`
- Execution order: 1st of 6
- Prerequisites: none
- Subsequent changes: `pyde-appearance-watermark`, `pyde-system-variables-parameter-contract`

## Why

All subsequent capability changes share a common foundation: persistent admin configuration, hardened API contracts, feature-flag boundaries, and well-defined permission exposure rules. Today, `SystemService` keeps several admin-facing settings (online maps, request timeouts, platform switches) in process-memory variables like `_online_maps` and `_system_params`. Any configuration written there vanishes on restart. No admin should trust a settings panel that loses state when the process cycles.

Beyond persistence, the current `/sysParameter/*`, `/setting/authentication/status`, `/engine/*`, and `/resource/checkPermission/*` endpoints lack stable response contracts and consistent auth enforcement. This makes it impossible for downstream changes (appearance, watermark, embedding, authentication) to build on a reliable foundation without each one reinventing its own settings storage and permission checks.

## What Changes

- Migrate `SystemService` memory-backed admin settings (`_online_maps`, `_system_params`, etc.) to persistent configuration contracts backed by `CoreSysSetting`.
- Unify `CoreSysSetting` key namespace conventions, default values, compatibility layers, and API response shapes.
- Define per-capability feature flags with default states, rollout rules, disabled-state behavior, and rollback boundaries.
- Harden management-plane API behavior for `/sysParameter/*`, `/setting/authentication/status`, `/engine/*`, and `/resource/checkPermission/*`.
- Produce a capability parity matrix mapping 8 unique capability domains to 6 changes, with current-status assessment (exists / partial / stub / missing).
- Inventory admin permission boundaries: menu exposure, resource-level ACL, public vs. authenticated vs. admin-only route classification.

## Capabilities

### New Capabilities

- `admin-config-foundation`: Persistent configuration backbone, unified key namespace, feature-flag registry, and admin permission boundary contracts shared by all subsequent changes.

### Modified Capabilities

- `backend-contract-compatibility`: Hardened response contracts and auth enforcement for system parameter, engine, and authentication status endpoints.

## Impact

- Affected backend code: `app/models/sys_setting.py`, `app/services/system_service.py`, `app/services/sys_setting_service.py`, `app/routers/system.py`, `app/routers/bootstrap.py`, `app/settings/config.py`, and related tests.
- Structured domains (watermark, sys_variable) retain their independent models; they are not folded back into `CoreSysSetting`.
- No frontend visual redesign. System settings pages continue using existing tab structure with new backing contracts.
- No new Alembic migration for `CoreSysSetting` itself (the table already exists), but any new structured keys may need seeding scripts.
- All subsequent changes depend on this one completing first.

## Non-goals

- Will not directly implement external identity-source login flows.
- Will not directly implement data filing workflows.
- Will not redesign the existing frontend system settings page visually.
- Will not change existing global token header semantics.
- Will not fold structured domains (watermark, sys_variable) back into `CoreSysSetting`.
- Will not copy DataEase brand assets, logos, marketing copy, or proprietary content.

## Gate Layer

- L0: `cd core/pydataease-backend && uv run ruff check .`
- L1: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
