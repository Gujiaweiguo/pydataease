## Why

CoreSysVariableValue has no `user_id` column — all variable values are global. The official DataEase manual expects per-user variable resolution (e.g., user A sees `store_name=蓝墨店`, user B sees `store_name=红叶店`). The runtime resolver in `_resolve_sysvar_rules()` currently does `del user` on line 301, discarding user context entirely. This is the last remaining product gap between our permission system and the official manual.

## What Changes

- Add nullable `user_id` (BigInteger) column to `core_sys_variable_value` table via Alembic migration
- Update `CoreSysVariableValue` model with `user_id` column
- Update Pydantic schemas to carry `userId` on create/edit/response
- Update `_resolve_sysvar_rules()` and `_fetch_sysvar_values()` to prefer user-specific values over global ones (priority: user-scoped > global > default deny)
- Apply same resolution pattern to `WatermarkService._system_variable_sources()`
- Implement the stub `personSysVariableInfo/{uid}` endpoint
- Add user selector to frontend sysvar value panel and value create/edit dialog
- Backend service CRUD accepts and persists `user_id` on value records

## Capabilities

### New Capabilities

- `per-user-sysvar-resolution`: Per-user variable value resolution with user-scoped priority fallback

### Modified Capabilities

- `sysvar-row-permission`: Resolution pipeline now considers user context when looking up variable values

## Impact

- **Database**: New migration adding nullable column — backward compatible, no data loss
- **API**: Existing value CRUD endpoints gain optional `userId` field; new endpoint `GET /user/personSysVariableInfo/{uid}`
- **Services**: `DataPermissionService._resolve_sysvar_rules()`, `WatermarkService._system_variable_sources()` — resolution logic change
- **Frontend**: `sys-variable/index.vue` value panel gains user column and user selector
- **Gate layer**: L0 (ruff + ts:check/lint) + L1 (pytest) + L2 (alembic upgrade head, docker build) — database migration and service logic changes
