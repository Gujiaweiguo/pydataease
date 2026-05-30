## Plan Reference

- PLAN_ID = `pydataease-dataease-capabilities-plan-v1`
- Execution order: 2nd of 6
- Prerequisites: `pyde-admin-config-foundation`
- Subsequent changes: `pyde-system-variables-parameter-contract`

## Why

Appearance configuration and watermarking are the first user-visible capabilities built on the persistent settings foundation. Today, the backend exposes partial appearance endpoints under `/sysParameter/ui` and `/sysParameter/basic`, but the configuration items are incomplete, some values reset on restart, and the watermark module operates without a unified runtime policy for public pages, share pages, and embedded contexts.

Without closing these gaps, every page that renders a theme color, site name, login background, footer, or watermark overlay either falls back to hardcoded defaults or reads from an unreliable source. Admins can't trust that their configuration changes will survive a restart or apply consistently across all viewing contexts (normal pages, login pages, share pages, embedded pages).

## What Changes

- Close appearance configuration gaps: define a complete inventory of configurable items (site name, theme color, navbar, login page assets, footer, help link, demo tip, font), their default values, persistence strategy, and read paths for each viewing context.
- Establish watermark runtime policy: admin save contract, public read contract, display rules for normal/share/embed pages with and without login state, text template placeholder integration with system variables.
- Wire both capabilities to the feature-flag and rollback registry from Change 1, so disabling appearance or watermark flags returns the system to safe defaults without data loss.

## Capabilities

### New Capabilities

- `appearance-config`: Admin-configurable appearance settings with stable API, DTO, default values, and feature-flag control. Covers site name, theme, navbar, login page, footer, help link, demo tip, and font configuration.
- `watermark-runtime`: Watermark configuration and runtime display policy governing when and how watermarks appear on normal, shared, and embedded pages, with text template placeholder support.

### Modified Capabilities

- `backend-contract-compatibility`: Extended route/auth coverage for appearance and watermark read/write endpoints with consistent `ResultMessage` wrapping.

## Impact

- Affected backend code: `app/routers/watermark.py`, `app/services/watermark_service.py`, `app/models/watermark.py`, `app/services/sys_setting_service.py`, `app/services/system_service.py`, `app/routers/bootstrap.py`, and related tests.
- Frontend system settings tabs continue using existing structure; configuration backing contracts change but tab layout does not.
- No Alembic migration for `CoreSysSetting` (table exists). Watermark model is already present; only configuration surface may expand.
- Watermark text templates will integrate with system variable placeholders (deferred detail to Change 3 contract).
- Configuration changes apply to all viewing contexts: normal pages, login pages, share pages, embedded pages.

## Non-goals

- Will not copy DataEase brand resources, logos, or proprietary marketing content.
- Will not rebuild the entire frontend theming system.
- Will not fork watermark logic into multiple runtime versions.
- Will not let public query endpoints expose unnecessary sensitive information.
- Will not redesign the system settings page UI layout.

## Gate Layer

- L0: `cd core/pydataease-backend && uv run ruff check .`
- L1: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- L0 (frontend, only when admin UI is touched): `cd core/core-frontend && npm run ts:check && npm run lint`
