## 1. SysVariable Data Layer

- [x] 1.1 Create `app/models/sys_variable.py` with `CoreSysVariable` and `CoreSysVariableValue` models and export them from `app/models/__init__.py`
- [x] 1.2 Create `app/schemas/sys_variable.py` request/response DTOs with camelCase-compatible aliases for variable and value CRUD
- [x] 1.3 Create `app/repositories/sys_variable_repo.py` with async CRUD, query, and paging helpers for variables and variable values

## 2. SysVariable Service and Routes

- [x] 2.1 Create `app/services/sys_variable_service.py` with definition CRUD, value CRUD, pagination, and dependency provider
- [x] 2.2 Create `app/routers/sys_variable.py` with all 11 `sysVariable` endpoints and auth-protected dependency injection
- [x] 2.3 Register the new router in `app/main.py`

## 3. SysParameter Compatibility

- [x] 3.1 Extend `app/services/system_service.py` and/or `app/services/sys_setting_service.py` to support missing online-map and default/share/UI/login helpers
- [x] 3.2 Add any missing `sysParameter` routes so `/queryOnlineMap/{type}`, `/shareBase`, `/ui`, `/defaultSettings`, and `/defaultLogin` are available with wrapped responses

## 4. Contract Tests

- [x] 4.1 Add `tests/test_sys_variable_routes.py` covering route registration, wrapped responses, and auth failures for representative `sysVariable` endpoints
- [x] 4.2 Extend or add route tests for the completed `sysParameter` endpoints if current coverage does not already exercise them

## 5. Verification

- [x] 5.1 `cd core/pydataease-backend && uv run ruff check .`
- [x] 5.2 `cd core/pydataease-backend && uv run pytest tests/test_sys_variable_routes.py -v`
- [x] 5.3 `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
- [x] 5.4 Note that broader L1 regression (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`) is recommended for this API/repository change but deferred from this session unless explicitly requested
