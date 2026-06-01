## Context
The permission management system has a complete skeleton but 7 implementation gaps vs the official manual. The current system uses a three-layer grant model (CoreRolePermission, CoreUserPermission, CoreOrgPermission) for menu permissions and CoreResourceAcl for resource-level permissions. Row/column permissions use dedicated tables. The frontend uses v-permission directive checking menuAuth && anyManage.

Key files:
- Backend: permission_service.py, data_permission_service.py, auth_permission_service.py, org_service.py, menu_service.py
- Frontend: directive/Permission/index.ts, store/modules/interactive.ts
- Models: CorePermissionPoint, CoreResourceAcl, CoreRowPermission, CoreColumnPermission

## Goals / Non-Goals
Goals:
- Close all P0 gaps that can cause unauthorized access or data exposure
- Align implementation with documented product semantics
- Make permission enforcement happen at backend, not just frontend

Non-Goals:
- Complete rearchitecting of the permission model
- Changing the database schema for core permission tables (except column_permission mask fields)
- Touching the xpack submodule

## Decisions

### D1: Resource enforcement via dependency injection
Use FastAPI's Depends() with the existing require_resource() dependency from dependencies/permission.py. Each resource router endpoint that performs mutations (create, edit, delete, export) gets the dependency added. Read-only endpoints use require_resource with "view" permission_type.

Rationale: The dependency already exists but is unused. Using it is the minimal-change approach.

Alternative: Middleware-level enforcement - rejected because it's harder to scope per-endpoint permission types.

### D2: Sysvar resolution in DataPermissionService
Add a new private method _resolve_sysvar_rules() that:
1. Queries `CoreSysVariable` + `CoreSysVariableValue` for the current effective variable values (current implementation uses the first available value because the value model has no `user_id` dimension yet)
2. For each sysvar-type row permission rule, substitutes the variable name in `filter_sql` with a SQL-safe literal value
3. Returns the resolved filter fragments

Rationale: Keeps sysvar logic in the same service that already handles row filtering.

Implementation note: the shipped fix also extends this execution chain to external MySQL datasource dataset reads, so `previewData` and `enumValue` now apply the same row/column permission semantics as internal SQL execution.

### D3: Org tree scope narrowing
Change OrgService.tree() for non-admin users to return only the user's own org node (no ancestors, no descendants). Add a separate method tree_with_context() if broader visibility is needed for navigation.

Rationale: Matches manual's "strict isolation" semantics. Current ancestor+descendant expansion exceeds documented scope.

### D4: Datasource view-only enforcement
In dataset create/edit service methods, check if the user's effective permission on the linked datasource is "view" only (weight < 2). If so, raise 403.

Rationale: Backend enforcement is the only reliable way to prevent API-level bypass.

### D5: Column mask parameterization
Add mask_start (int, default 0) and mask_end (int, default -1) fields to CoreColumnPermission. The masking function uses these to determine the character range to replace. Frontend adds inputs for these fields in the column permission dialog.

Rationale: Directly matches the manual's "mask from position M to position N" requirement.

Implementation note: the final runtime fix also aligns external datasource enum queries with trusted physical field names (`origin_name`) so masked enum results can be generated for datasets whose display fields use non-ASCII identifiers such as `店铺`.

### D6: Frontend capability model
Extend interactiveStore to store per-resource-type capabilities (canView, canManage, canAuthorize, canExport) derived from the weight value. Update v-permission to accept capability strings like 'dataset:export'.

Rationale: Minimal frontend change that aligns with the existing weight-based backend model.

### D7: Menu permission role-only enforcement
In PermissionService.get_effective_menu_ids(), skip the user-direct and org-level grant/deny steps. Keep the tables for data compatibility but stop reading them for menu decisions.

Rationale: Aligns implementation with documented "menu permissions bind to roles only" semantics.

## Risks / Trade-offs

- [Risk: Breaking existing API consumers who rely on permissive checks] -> Mitigation: Add permission_enforcement_enabled config flag (already exists), default True in production
- [Risk: Org tree narrowing breaks admin workflows that navigate across orgs] -> Mitigation: Admin (user_id=1) bypasses all restrictions; only non-admin scope changes
- [Risk: Sysvar resolution performance for large variable sets] -> Mitigation: Cache user variable values per session; variable count is expected to be small (<100)
- [Risk: Column permission migration adds fields to existing table] -> Mitigation: Alembic migration with nullable new fields and sensible defaults
