## Why

After successful login, the frontend calls `GET /menu/query` to get the navigation menu tree, which determines the entire sidebar structure and route permissions. Without this endpoint, the frontend shows "缺少菜单权限" and cannot render the dashboard. This is the critical blocker for a working end-to-end user experience.

## What Changes

- **Menu model + migration**: Create `core_menu` table with seed data matching the Java backend's menu structure
- **Menu query endpoint**: `GET /de2api/menu/query` returning the full menu tree as `MenuVO[]`
- **Additional workbranch stubs**: `GET /sysParameter/shareBase`, `GET /templateMarket/searchRecommend`, `POST /dataVisualization/interactiveTree` — to let the workbranch page render
- **Typeface stubs**: `GET /typeface/defaultFont`, `GET /typeface/listFont` — to eliminate 404 errors

## Capabilities

### New Capabilities
- `menu-system`: Menu tree query endpoint that returns navigation structure for the frontend

### Modified Capabilities
- `frontend-backend-integration`: Additional stub endpoints needed for workbranch page rendering

## Impact

- **Database**: New `core_menu` table + Alembic migration with seed data
- **Backend**: New menu router, service, repository, and model
- **Bootstrap router**: Additional stub endpoints (shareBase, typeface, templateMarket, interactiveTree)
- **Tests**: New menu route tests
