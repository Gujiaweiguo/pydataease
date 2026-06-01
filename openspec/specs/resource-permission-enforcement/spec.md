# Capability: resource-permission-enforcement

## REQUIREMENTS
1. Every backend endpoint that creates, edits, deletes, or exports a dashboard/screen/dataset/datasource MUST call require_resource_access or equivalent before performing the operation.
2. The /resource/checkPermission/{resource_id} endpoint MUST perform actual permission validation instead of always returning True.
3. Read operations on resources MUST check "view" permission; mutation operations MUST check "manage" permission; export operations MUST check "export" permission type.
4. Admin users (user_id=1) bypass all permission checks as before.
5. When permission_enforcement_enabled is False, all checks are skipped (existing behavior preserved).

## ACCEPTANCE CRITERIA
- Non-admin user without manage permission receives 403 on resource mutation endpoints
- Non-admin user with view-only permission can read but not mutate resources
- Admin user can perform all operations regardless of permission configuration
- checkPermission endpoint returns False when user lacks permission
