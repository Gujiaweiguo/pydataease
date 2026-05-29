## Why

With users, roles, and orgs manageable (Change 2), the system still lacks a permission configuration UI. Backend permission evaluation already works (`permission_service.py`, `auth_permission_service.py`), but there's no frontend interface for admins to assign/revoke menu and resource permissions per role or user. This change adds the permission management console.

## What Changes

- Build menu permission tree UI: display full menu tree with checkboxes for granting/revoking per role or user
- Build resource permission tree UI: display resource tree (dashboard/screen/dataset/datasource) with permission type selectors (use/manage/authorize/view/export)
- Wire to existing `api/auth.ts` permission configuration endpoints
- Verify `/menu/query` responds differently after permission changes (dynamic menu filtering)
- Calibrate org admin vs super admin authorization boundaries (`_can_manage_auth`)
- Verify cross-org isolation: no permission leakage between organizations

## Plan Context

- **Plan ID**: `pydataease-access-control-plan-v1`
- **Plan file**: `.sisyphus/plans/pydataease-access-control-plan-v1.md`
- **Depends on**: `user-role-center`
- **Followed by**: `permission-row-column`
- **Tasks in plan**: T10 (menu/resource permission config UI), T11 (authorization boundary calibration)

## Capabilities

### New Capabilities
- `permission-config-ui`: Frontend console for configuring menu and resource permissions per role/user, with tree display and grant/revoke interaction.

### Modified Capabilities
- `menu-query`: No backend changes — already supports permission filtering.
- `auth-boundary`: May need minor calibration of `_can_manage_auth` for org admin vs super admin.

## Impact

- Frontend: new Vue pages/sections in `src/views/system/permission/` for permission configuration.
- Uses existing API clients in `api/auth.ts`.
- Minimal or no backend changes — permission services already exist.
- Gate layers: L0 frontend + L0 backend (if minor calibrations) + L2 frontend (routing)
