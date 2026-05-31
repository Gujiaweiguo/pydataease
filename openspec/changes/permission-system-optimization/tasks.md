## TODOs

### P0: Resource Permission Enforcement Closure
- [x] Wire require_resource_access into dashboard router endpoints (create, edit, delete, export)
- [x] Wire require_resource_access into screen router endpoints (create, edit, delete, export)
- [x] Wire require_resource_access into dataset router endpoints (create, edit, delete, export)
- [x] Wire require_resource_access into datasource router endpoints (create, edit, delete, export)
- [x] Replace checkPermission stub in bootstrap.py with actual permission check
- [x] Add backend tests for resource permission enforcement (403 for unauthorized, 200 for authorized)

### P0: Sysvar Row Permission Execution
- [ ] Add _resolve_sysvar_rules() method to DataPermissionService
- [ ] Integrate sysvar resolution into collect_row_filters() with correct priority (user > sysvar > role > org)
- [ ] Add tests for sysvar row permission resolution

### P0: Organization Isolation Correction
- [ ] Modify OrgService.tree() to return only user's own org for non-admin
- [ ] Add tests verifying non-admin sees only their own org

### P0: Datasource View-Only Guard
- [ ] Add permission check in dataset create service method (check datasource manage permission)
- [ ] Add permission check in dataset edit service method (check datasource manage permission)
- [ ] Add tests for datasource view-only enforcement

### P1: Column Permission Custom Mask
- [ ] Add Alembic migration for mask_start, mask_end fields on core_column_permission
- [ ] Update CoreColumnPermission model with mask_start, mask_end columns
- [ ] Update ColumnPermissionService to handle mask_start/mask_end
- [ ] Update DataPermissionService.apply_column_rules() to use mask_start/mask_end
- [ ] Update column permission schemas (create/update/response) with mask fields
- [ ] Update frontend RowColumnPermission.vue with mask range configuration UI
- [ ] Add tests for custom mask range behavior

### P1: Frontend Permission Granularity
- [ ] Extend interactiveStore with per-resource capability flags (canView, canManage, canAuthorize, canExport)
- [ ] Update v-permission directive to accept 'resource:capability' format
- [ ] Maintain backward compatibility with existing v-permission="['panel']" syntax
- [ ] Update affected views to use new capability syntax where appropriate

### P2: Menu Permission Model Alignment
- [ ] Modify PermissionService.get_effective_menu_ids() to skip user-direct and org-level grant/deny steps
- [ ] Add test verifying menu visibility is role-only
- [ ] Update auth_permission_service.py if any menu save logic references user/org dimensions

## Final Verification Wave

- [ ] F1: All backend tests pass (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`)
- [ ] F2: Ruff check passes (`uv run ruff check .`)
- [ ] F3: Alembic migration succeeds (`uv run alembic upgrade head`)
- [ ] F4: Manual review of all changed files for correctness and security
