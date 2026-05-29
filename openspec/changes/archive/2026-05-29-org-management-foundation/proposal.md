## Why

The pydataease backend has organization, user, role, and permission services already implemented, but the admin console is invisible in the frontend. Root cause: `core_menu` lacks admin console menu seeds (only 10 rows for workbranch/panel/screen/data), `core_permission_point` lacks admin permission points (only 9 rows), `menu_service.py` TITLE_MAP doesn't cover new admin entries, and `src/views/system/` lacks org/user/role/permission pages (only parameter/font/modify-pwd exist). This change fixes the "frontend shows nothing" problem by establishing the admin visibility foundation and organization management base UI.

## What Changes

- Extend `core_menu` seeds: add system/org/user/role/permission menu nodes with proper pid/path/component/menu_sort/hidden/auth values
- Extend `core_permission_point` seeds: add admin console permission points for menu authorization
- Update `menu_service.py` TITLE_MAP: add titles for new admin console entries
- Create frontend page skeletons in `src/views/system/`: org/, user/, role/, permission/ — each with minimal `index.vue` that renders a container/placeholder
- Verify `/menu/query` returns the full admin console tree for admin user
- Verify dynamic route mapping via `generateRoutesFn2()` resolves to existing view components
- Wire org management base page to existing `api/org.ts` for org tree display

## Plan Context

- **Plan ID**: `pydataease-access-control-plan-v1`
- **Plan file**: `.sisyphus/plans/pydataease-access-control-plan-v1.md`
- **Depends on**: existing backend org/user/role/auth infrastructure (no prior OpenSpec change)
- **Followed by**: `user-role-center`
- **Tasks in plan**: T1 (solidify baseline), T2 (root cause), T3 (confirm split), T4 (menu/permission-point design), T5 (title/route alignment), T6 (system page skeletons)

## Capabilities

### New Capabilities
- `admin-visibility`: Admin console menu seeds, permission points, title mapping, and minimal page skeletons that make org/user/role/permission entries visible and reachable in the frontend.
- `org-management-ui`: Organization tree display and basic CRUD wiring to existing backend APIs.

### Modified Capabilities
- `menu-query`: `/menu/query` returns admin console entries for authorized users.
- `title-mapping`: TITLE_MAP in `menu_service.py` covers admin console entry titles.

## Impact

- Alembic migration to seed `core_menu` and `core_permission_point` rows for admin console.
- Backend: `menu_service.py` TITLE_MAP expansion.
- Frontend: new Vue pages in `src/views/system/` for org/user/role/permission.
- Gate layers: L0 backend + L0 frontend + L1 backend + L2 backend (new migration) + L2 frontend (routing changes)
