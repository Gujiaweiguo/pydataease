## 1. Backend — API Key 认证基础设施

- [x] 1.1 在 `app/settings/defaults.py` 的 `SETTINGS_DEFAULTS` 中新增 `sqlbot.mode`（默认 `"basic"`）和 `sqlbot.apiKey`（默认空字符串）
- [x] 1.2 在 `app/services/sys_setting_service.py` 的 `get_sqlbot_settings` / `save_sqlbot_settings` 中扩展支持 `mode` 和 `apiKey` 字段
- [x] 1.3 创建 `app/dependencies/mysqlbot_auth.py`，实现 `verify_mysqlbot_apikey` FastAPI 依赖：读取请求 `X-API-Key` header，与 DB 中 `sqlbot.apiKey` 常量时间比较，缺失返回 401 "Missing API Key"，不匹配返回 401 "Invalid API Key"
- [x] 1.4 在 `app/middleware/whitelist.py` 的 `WHITE_PREFIXES` 中新增 `/mysqlbot/api/`，使 AuthMiddleware 跳过该前缀的 JWT 校验

## 2. Backend — MySQLBot 高级小助手回调 API

- [x] 2.1 创建 `app/schemas/mysqlbot.py`，定义 Pydantic schemas：`MysqlBotDatasource` 匹配 MySQLBot `AssistantOutDsSchema`（含 id, name, type, host, port, dataBase, user, password, extraParams, db_schema, tables 等字段）
- [x] 2.2 创建 `app/services/mysqlbot_service.py`，实现 `MysqlBotService`：
  - `list_datasources()` — 查询所有非 folder 类型数据源，从 `core_datasource.configuration` JSONB 提取完整连接凭据，返回 `list[MysqlBotDatasource]`
  - `list_tables(datasource_id)` — 验证数据源存在，获取表列表
  - `list_fields(datasource_id, table_name)` — 验证数据源存在，获取字段元数据
  - `execute_query(datasource_id, sql)` — 验证数据源存在，只读 SQL 校验 + 行数限制 + 执行
- [x] 2.3 创建 `app/routers/mysqlbot.py`，定义 4 个端点，全部使用 `Depends(verify_mysqlbot_apikey)`：
  - `GET /mysqlbot/api/datasources` → `list_datasources()` **(主端点，MySQLBot 高级小助手实际调用)**
  - `GET /mysqlbot/api/datasources/{datasource_id}/tables` → `list_tables()`
  - `GET /mysqlbot/api/datasources/{datasource_id}/tables/{table_name}/fields` → `list_fields()`
  - `POST /mysqlbot/api/datasources/{datasource_id}/query` → `execute_query()`
- [x] 2.4 在 `app/main.py` 中注册新路由：`api_router.include_router(mysqlbot_router)`

## 3. Backend — 测试

- [x] 3.1 创建 `tests/test_mysqlbot_auth.py`：测试 `verify_mysqlbot_apikey` 依赖的 3 个场景（有效 Key、缺失 Key、错误 Key）
- [x] 3.2 创建 `tests/test_mysqlbot_api.py`：使用 `app.dependency_overrides` mock `MysqlBotService`，测试 4 个端点的完整 API 契约（含 200/400/401/404 场景），覆盖 specs 中定义的全部场景

## 4. Frontend — 系统设置 UI 更新

- [x] 4.1 在 `src/locales/zh-CN.ts`、`en.ts`、`tw.ts` 中新增 i18n key：`sqlbot.mode`（基础/高级）、`sqlbot.apiKey`（接口密钥）、`sqlbot.mode_basic`、`sqlbot.mode_advanced`、`sqlbot.apiKey_placeholder`
- [x] 4.2 更新 `src/views/system/parameter/third-party/ThirdEdit.vue`：在表单中新增模式选择（Radio：基础/高级），高级模式下显示 API Key 输入框，保存时将 `mode` 和 `apiKey` 一并提交
- [x] 4.3 更新 `src/views/system/parameter/third-party/index.vue`：卡片上显示当前模式标签（基础/高级）

## 5. 验证

- [x] 5.1 运行 `uv run ruff check .` 确保后端 lint 通过
- [x] 5.2 运行 `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` 确保全部测试通过（15/15）
- [x] 5.3 运行 `npm run lint`（前端目录）确保前端 lint 通过

## 6. 集成测试

- [x] 6.1 本地 E2E 模拟：模拟 MySQLBot `convert2schema()` 对 `/datasources` 端点的调用，验证 11 个数据源全部返回完整凭据
- [x] 6.2 MySQLBot 远程 API 探索：登录 sqlbot.lanlnk.cn:8000，创建测试高级小助手（id: 7467226977301172224），确认 pydataease 无公网 IP 无法完成真实回调
