## Why

With admin console visibility established (Change 1), the org/user/role/permission pages are visible but only show placeholder content. This change wires the user management and role management pages to existing backend APIs, completing the user-role management frontend loop. The backend APIs already exist (`/user/*`, `/role/*`) — the gap is frontend UI interaction.

## What Changes

- Wire user management page to `api/user.ts`: user list with pagination, create user, edit user, enable/disable user, reset password, batch delete
- Wire role management page to `api/user.ts` role endpoints: role list, create role, edit role, delete role
- Implement user-role binding UI: mount users to roles, unmount users from roles, external user search and mount
- Implement org-scoped views: current org context constrains all user/role queries
- Handle edge cases: deleting last role across all orgs removes user; built-in roles cannot be edited/deleted; duplicate account rejection
- Ensure stub capabilities (e.g., batch import) are explicitly marked as not-yet-implemented

## Plan Context

- **Plan ID**: `pydataease-access-control-plan-v1`
- **Plan file**: `.sisyphus/plans/pydataease-access-control-plan-v1.md`
- **Depends on**: `org-management-foundation`
- **Followed by**: `permission-menu-resource`
- **Tasks in plan**: T7 (org management UI), T8 (user management UI), T9 (role management UI)

## Capabilities

### New Capabilities
- `user-management-ui`: Frontend user CRUD with org-scoping, search, enable/disable, password reset, batch delete.
- `role-management-ui`: Frontend role CRUD with org-scoping, built-in vs custom distinction, user-role binding UI.
- `org-management-ui-completion`: Organization tree display and CRUD wired to existing backend APIs.

### Modified Capabilities
- `user-management`: No backend changes — existing APIs are sufficient.
- `role-management`: No backend changes — existing APIs are sufficient.

## Impact

- Frontend-only change: modifies Vue pages in `src/views/system/` for user, role, and org management.
- Uses existing API clients in `api/user.ts`, `api/org.ts`.
- No new backend endpoints needed.
- Gate layers: L0 frontend + L2 frontend (routing/view changes)
