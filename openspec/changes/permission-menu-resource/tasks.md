## 1. Permission Catalog and Migration

- [ ] 1.1 Create `CorePermissionPoint` model (`core_permission_point` table) mapping menu/resource to permission types (use/manage/authorize/view/export).
- [ ] 1.2 Create `CoreRolePermission` model (`core_role_permission` table) binding role to permission point with grant/deny.
- [ ] 1.3 Create `CoreUserPermission` model (`core_user_permission` table) for direct user-level permission overrides.
- [ ] 1.4 Create `CoreOrgPermission` model (`core_org_permission` table) for org-level permission defaults.
- [ ] 1.5 Write Alembic migration for all permission tables with expand-first approach.
- [ ] 1.6 Seed default permission catalog matching existing menu items and resource types.

## 2. Menu Authorization

- [ ] 2.1 Modify `MenuService.get_menu_tree()` to accept user context and filter menus by effective permissions.
- [ ] 2.2 Implement effective-permission computation: union of org grants + role grants + user direct grants.
- [ ] 2.3 Ensure system-admin sees all menus regardless of explicit grants.
- [ ] 2.4 Verify `/menu/query` returns different menus for admin vs non-admin users.

## 3. Resource Authorization

- [ ] 3.1 Implement permission check decorator/dependency for resource routers (dashboard, screen, dataset, datasource).
- [ ] 3.2 Add permission enforcement to `GET /visualization/tree`, `GET /dataset/tree`, `GET /datasource/list` endpoints.
- [ ] 3.3 Add permission enforcement to write operations (create/edit/delete resource).
- [ ] 3.4 Return 403 for unauthorized access (not 404 or 500).

## 4. Guardrails and Compatibility

- [ ] 4.1 Add feature flag to disable permission enforcement (fall back to auth-only mode).
- [ ] 4.2 Preserve existing `/menu/query` contract shape (same response structure, just filtered content).
- [ ] 4.3 Verify login, token refresh, and embedded/share flows still work with permission layer active.

## 5. Verification

- [ ] 5.1 `cd core/pydataease-backend && uv run ruff check .` — zero errors.
- [ ] 5.2 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass.
- [ ] 5.3 Browser test: non-admin user sees filtered menu; admin sees all menus.
- [ ] 5.4 API test: non-admin access to restricted resource returns 403.
