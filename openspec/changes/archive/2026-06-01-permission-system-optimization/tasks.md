## TODOs

### P0: Resource Permission Enforcement Closure
- [x] Wire require_resource_access into dashboard router endpoints (create, edit, delete, export)
- [x] Wire require_resource_access into screen router endpoints (create, edit, delete, export)
- [x] Wire require_resource_access into dataset router endpoints (create, edit, delete, export)
- [x] Wire require_resource_access into datasource router endpoints (create, edit, delete, export)
- [x] Replace checkPermission stub in bootstrap.py with actual permission check
- [x] Add backend tests for resource permission enforcement (403 for unauthorized, 200 for authorized)

### P0: Sysvar Row Permission Execution
- [x] Add _resolve_sysvar_rules() method to DataPermissionService
- [x] Integrate sysvar resolution into collect_row_filters() with correct priority (user > sysvar > role > org)
- [x] Add tests for sysvar row permission resolution

### P0: Organization Isolation Correction
- [x] Modify OrgService.tree() to return only user's own org for non-admin
- [x] Add tests verifying non-admin sees only their own org

### P0: Datasource View-Only Guard
- [x] Add permission check in dataset create service method (check datasource manage permission)
- [x] Add permission check in dataset edit service method (check datasource manage permission)
- [x] Add tests for datasource view-only enforcement

### P1: Column Permission Custom Mask
- [x] Add Alembic migration for mask_start, mask_end fields on core_column_permission
- [x] Update CoreColumnPermission model with mask_start, mask_end columns
- [x] Update ColumnPermissionService to handle mask_start/mask_end
- [x] Update DataPermissionService.apply_column_rules() to use mask_start/mask_end
- [x] Update column permission schemas (create/update/response) with mask fields
- [x] Update frontend RowColumnPermission.vue with mask range configuration UI
- [x] Add tests for custom mask range behavior

### P1: Frontend Permission Granularity
- [x] Extend interactiveStore with per-resource capability flags (canView, canManage, canAuthorize, canExport)
- [x] Update v-permission directive to accept 'resource:capability' format
- [x] Maintain backward compatibility with existing v-permission="['panel']" syntax
- [x] Update affected views to use new capability syntax where appropriate

### P2: Menu Permission Model Alignment
- [x] Modify PermissionService.get_effective_menu_ids() to skip user-direct and org-level grant/deny steps
- [x] Add test verifying menu visibility is role-only
- [x] Update auth_permission_service.py if any menu save logic references user/org dimensions

## Final Verification Wave

- [x] F1: Targeted backend regression tests pass for permission runtime wiring (`uv run pytest tests/test_sysvar_row_permission.py tests/test_dataset_service_unit.py tests/test_dataset_datasource_integration.py -v`)
- [x] F2: Targeted Ruff checks pass for changed backend files and new integration coverage (`uv run ruff check app/services/data_permission_service.py app/services/dataset_service.py tests/test_sysvar_row_permission.py tests/test_dataset_service_unit.py tests/test_dataset_datasource_integration.py`)
- [x] F3: Live restricted-user verification passes for external MySQL datasource runtime behavior
  - `POST /de2api/datasetData/previewData` returns only `蓝墨店` rows and masks `店铺` as `蓝*店`
  - `POST /de2api/datasetData/enumValue` returns `["蓝*店"]`
- [x] F4: Added real MySQL datasource integration coverage for `preview_data()` and `get_enum_values()` with sysvar row filter + column mask
