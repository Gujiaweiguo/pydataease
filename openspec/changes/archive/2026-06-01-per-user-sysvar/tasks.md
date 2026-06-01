## 1. Database & Model

- [ ] 1.1 Add Alembic migration adding nullable `user_id` (BigInteger) column to `core_sys_variable_value` table
- [ ] 1.2 Update `CoreSysVariableValue` model in `app/models/sys_variable.py` with `user_id` column

## 2. Schemas & Service CRUD

- [ ] 2.1 Add `user_id` / `userId` field to `SysVariableValueCreateRequest`, `SysVariableValueEditRequest`, `SysVariableValueResponse` in `app/schemas/sys_variable.py`
- [ ] 2.2 Update `SysVariableService.create_value()` / `edit_value()` to persist `user_id`
- [ ] 2.3 Update `SysVariableValueRepository` queries to support filtering by `user_id`

## 3. Runtime Resolution

- [ ] 3.1 Modify `_fetch_sysvar_values()` in `data_permission_service.py` to accept `user_id` and prefer user-scoped values (ORDER BY user_id IS NULL ASC)
- [ ] 3.2 Remove `del user` in `_resolve_sysvar_rules()` and pass `user.id` to `_fetch_sysvar_values()`
- [ ] 3.3 Apply same resolution pattern to `WatermarkService._system_variable_sources()`
- [ ] 3.4 Implement `personSysVariableInfo/{uid}` endpoint in user router

## 4. Frontend

- [ ] 4.1 Add `userId` field to value create/edit API payloads in `variable.ts`
- [ ] 4.2 Add user selector (el-select with search) to value create/edit dialog in `sys-variable/index.vue`
- [ ] 4.3 Add user name column to value list table (show "全局" for global values)
- [ ] 4.4 Implement `personSysVariableInfoApi` usage for user variable preview

## 5. Tests

- [ ] 5.1 Add unit tests for per-user sysvar resolution priority (user-scoped > global > default deny)
- [ ] 5.2 Update `test_sysvar_row_permission.py` to cover user-scoped resolution
- [ ] 5.3 Add route tests for value CRUD with `userId`
- [ ] 5.4 Add route test for `personSysVariableInfo/{uid}` endpoint

## 6. Verification

- [ ] 6.1 `uv run ruff check .` passes
- [ ] 6.2 `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` passes
- [ ] 6.3 `uv run alembic upgrade head` succeeds
- [ ] 6.4 `npm run ts:check` + `npm run lint` pass
