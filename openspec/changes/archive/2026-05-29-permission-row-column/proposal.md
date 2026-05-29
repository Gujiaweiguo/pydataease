## Why

With menu and resource permissions configurable (Change 3), the remaining gap is data-level security: row permissions control which rows a user can see, column permissions control field visibility and masking. Backend services for row/column permissions already exist (`row_permission_service.py`, `column_permission_service.py`, `data_permission_service.py`), but there's no frontend interface for managing these rules. This change adds the row/column permission management UI and verifies query-time enforcement.

## What Changes

- Build row permission rule UI: list/create/edit/delete row filter rules per dataset, targeting org/role/user/system-variable
- Build column permission rule UI: list/create/edit/delete column rules per dataset with actions (disable/desensitize/mask)
- Build whitelist configuration UI: exempt specific users from row/column rules
- Wire to existing row/column permission backend APIs
- Verify query-time enforcement: row filters actually reduce query results, column rules actually hide/mask fields
- Verify whitelist bypass behavior

## Plan Context

- **Plan ID**: `pydataease-access-control-plan-v1`
- **Plan file**: `.sisyphus/plans/pydataease-access-control-plan-v1.md`
- **Depends on**: `permission-menu-resource`
- **Followed by**: none (final change in the plan)
- **Tasks in plan**: T12 (row/column permission UI), T13 (execution verification)

## Capabilities

### New Capabilities
- `row-column-permission-ui`: Frontend console for configuring row permissions, column permissions, and whitelist exemptions per dataset.
- `permission-enforcement-verification`: Evidence that row/column rules actually affect query results.

### Modified Capabilities
- `sql-execution-engine`: No changes needed — already supports row/column injection.

## Impact

- Frontend: new Vue pages/sections in `src/views/system/permission/` for row/column rule management.
- Uses existing backend row/column permission services.
- Verification involves running actual queries and comparing results.
- Gate layers: L0 frontend + L0 backend + L1 backend + L2 frontend
