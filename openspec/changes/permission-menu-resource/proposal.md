## Why

With orgs, users, and roles in place, the system still has no authorization layer. The menu tree is delivered to all authenticated users without filtering, and backend APIs only check authentication (token valid + user enabled), not authorization (does this user have permission for this resource). This change builds the permission evaluation core.

## What Changes

- Add a permission catalog model that maps menu items and resource types to permission points.
- Implement menu authorization: `/menu/query` returns only menus the user has permission for (based on org + role + user grants).
- Implement resource authorization: backend APIs for dashboards, screens, datasets, and datasources check user permissions before returning data.
- Implement effective-permission computation: union of org-level, role-level, and user-direct grants.
- Add backend enforcement middleware or decorator that rejects unauthorized API access.
- Keep existing auth flow working; permission check is additive, not replacing authentication.

## Plan Context

- **Plan ID**: `pydataease-system-management-roadmap-v1`
- **Plan file**: `.sisyphus/plans/pydataease-system-management-roadmap-v1.md`
- **Depends on**: `org-management-foundation`, `user-role-center`
- **Followed by**: `permission-row-column`
- **Phase in plan**: Phase E — task T7

## Capabilities

### New Capabilities
- `menu-authorization`: Filter menu tree by user's effective permissions; unauthorized menus are hidden.
- `resource-authorization`: Check user permissions for business resources (dashboard, screen, dataset, datasource) at API level.

### Modified Capabilities
- `menu-query`: `/menu/query` changes from "return all menus" to "return authorized menus only."
- `auth-middleware`: Extends from identity-only to identity + authorization check.

## Impact

- Adds permission catalog tables and user/org/role permission grant tables via migration.
- Modifies `MenuService.get_menu_tree()` to accept user context and filter by permissions.
- Adds permission enforcement to existing resource routers (visualization, dataset, datasource, chart).
- Frontend menu rendering already handles dynamic menus; no structural frontend change needed for menu filtering.
- Verification: L0 backend + L1 backend + L2 backend + L2 frontend (menu behavior).
