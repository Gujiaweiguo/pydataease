## 1. Menu Model + Migration

- [x] 1.1 Create CoreMenu SQLAlchemy model in `app/models/system.py` (id BigInteger PK, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth)
- [x] 1.2 Create Alembic migration `a1b2c3d4e5f6` for `core_menu` table with 10 community seed rows matching Java V2.0__core_ddl.sql
- [x] 1.3 Create MenuRepository in `app/repositories/system_repo.py` that loads all menus ordered by menu_sort

## 2. Menu Service + Router

- [x] 2.1 Create `app/services/menu_service.py` with tree-building logic (group by pid → build tree → convert to MenuVO, handles type=1 directory + type=2 page nodes)
- [x] 2.2 Wire `GET /menu/query` in `app/routers/system.py` with MenuService (auth required)
- [x] 2.3 Create MenuVO + MenuMeta response schema in `app/schemas/menu.py`
- [x] 2.4 System router registered in `app/main.py` via api_router

## 3. Additional Bootstrap Stubs

- [x] 3.1 Add stub endpoints to `app/routers/bootstrap.py`: `GET /sysParameter/shareBase`, `GET /typeface/defaultFont`, `GET /typeface/listFont`
- [x] 3.2 Add `GET /templateMarket/searchRecommend` stub
- [x] 3.3 Add `POST /dataVisualization/interactiveTree` stub

## 4. Tests + Verification

- [x] 4.1 Add menu route tests in `tests/test_menu_routes.py` (2 tests: authenticated returns 200, unauthenticated returns 401)
- [x] 4.2 Run full test suite: 162 passed, 17 skipped
- [x] 4.3 Restart backend, verify `GET /de2api/menu/query` returns valid menu tree with all 5 top-level items (workbranch, panel, screen, data, sys-setting)
- [x] 4.4 Browser E2E: login → verify sidebar renders with menu items (工作台/仪表板/数据大屏/数据准备/数据集/数据源 all visible)
