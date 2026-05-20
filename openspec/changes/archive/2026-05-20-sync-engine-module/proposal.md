## Why

前端已集成同步引擎模块页面，但 Python/FastAPI 后端尚未提供对应 `/sync/**` API，导致页面初始化和操作请求直接 404。先补齐一组受鉴权保护的空实现接口，可以在 SeaTunnel 真正接入前稳定前后端契约并解锁联调。

## What Changes

- 新增一个 `sync` FastAPI router，统一承载 30 个前端已调用的同步模块接口。
- 所有接口先返回稳定的占位响应：空列表、空对象、零计数或 `valid: false`，不接入 service/repository/数据库。
- 将 sync router 注册到 `/de2api` API 前缀下，保持现有响应包装和鉴权中间件行为。
- 新增路由测试，覆盖全部 30 个路径已注册，并校验代表性接口仍然要求 `X-DE-TOKEN` 鉴权。

## Capabilities

### New Capabilities
- `sync-engine-stub-api`: 为同步数据源、同步任务、任务日志和摘要统计提供前端可调用的占位 API 合约。

### Modified Capabilities
（无——本 change 通过新增 capability 补齐 sync 模块，不修改既有 spec 行为）

## Impact

- 影响代码：`core/pydataease-backend/app/main.py`、新增 `app/routers/sync.py`、新增 `tests/test_sync_routes.py`
- 影响 API：新增 `/de2api/sync/**` 共 30 个占位端点
- 依赖/系统：无新增外部依赖、无数据库迁移、无 SeaTunnel 集成
- 验证门禁：L0 backend（`uv run ruff check .`）+ L1 backend（针对新路由测试）；这是 API/鉴权契约变更，不需要 Docker、打包或可运行环境级验证
