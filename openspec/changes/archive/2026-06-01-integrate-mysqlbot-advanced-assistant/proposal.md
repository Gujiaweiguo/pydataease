## Why

当前 pydataease 集成 MySQLBot（SQLBot fork）仅使用**基础小助手模式**——纯 script 注入，后端 stub 端点返回空数组，MySQLBot 自行管理所有数据源和 AI 逻辑。这意味着用户必须在 MySQLBot 中重复配置数据库连接，且无法利用 pydataease 已有的数据源管理能力。

集成**高级小助手模式**可以让 MySQLBot 通过配置的 endpoint URL 回调 pydataease，获取数据源列表及其完整连接凭据。MySQLBot 拿到凭据后直连数据库执行 AI 生成的 SQL，用户在 MySQLBot 的 AI 对话中直接查询 pydataease 管理的数据源，无需重复配置。

## What Changes

- **新增后端 API 端点**：在 pydataease 后端新增 MySQLBot 高级小助手回调接口：
  - `GET /mysqlbot/api/datasources` — **主端点**，返回所有非 folder 数据源的完整连接凭据（host, port, dataBase, user, password, extraParams, db_schema），响应格式匹配 MySQLBot 的 `AssistantOutDsSchema`
  - `GET /mysqlbot/api/datasources/{id}/tables` — 表列表（bonus，MySQLBot 当前不使用）
  - `GET /mysqlbot/api/datasources/{id}/tables/{table}/fields` — 字段元数据（bonus）
  - `POST /mysqlbot/api/datasources/{id}/query` — 只读 SQL 执行（bonus）
- **新增认证机制**：使用独立的 API Key 认证（`X-API-Key` header），与 pydataease JWT 认证解耦。API Key 存储在 `sys_setting` 表中，使用常量时间比较（`hmac.compare_digest`）
- **数据源凭据提取**：从 `core_datasource.configuration` JSONB 字段提取连接凭据，处理不同数据源类型的 key 变体（`dataBase`/`database`、`username`/`user`、`extraParams`/`extraParameters`）
- **配置扩展**：扩展 `sqlbot.*` 系统设置，新增 `sqlbot.mode`（basic/advanced）、`sqlbot.apiKey`
- **前端设置页面更新**：ThirdEdit.vue 支持选择高级小助手模式，配置 API Key
- **白名单更新**：`/mysqlbot/api/` 前缀加入中间件白名单，使用独立 API Key 认证

## Capabilities

### New Capabilities

- `mysqlbot-advanced-api`: MySQLBot 高级小助手回调 API——主端点返回数据源完整连接凭据（匹配 `AssistantOutDsSchema`），bonus 端点提供表/字段/查询能力。API Key 认证，只读 SQL 安全约束
- `mysqlbot-credentials`: MySQLBot 接口凭证管理——存储和验证 API Key，支持在系统设置中配置

### Modified Capabilities

（无已有 spec 需要修改）

## Impact

**后端代码变更：**
- `app/routers/mysqlbot.py` — 新增路由文件（4 个端点）
- `app/services/mysqlbot_service.py` — 新增服务（凭据提取、元数据查询）
- `app/schemas/mysqlbot.py` — 新增 Pydantic schemas（匹配 `AssistantOutDsSchema`）
- `app/dependencies/mysqlbot_auth.py` — 新增 API Key 认证依赖
- `app/settings/defaults.py` — 新增 `sqlbot.mode`、`sqlbot.apiKey` 默认值
- `app/services/sys_setting_service.py` — 扩展 `get_sqlbot_settings`/`save_sqlbot_settings`
- `app/middleware/whitelist.py` — 新增 `/mysqlbot/api/` 白名单前缀
- `app/main.py` — 注册新路由

**前端代码变更：**
- `src/views/system/parameter/third-party/ThirdEdit.vue` — 新增模式选择和 API Key 配置
- `src/views/system/parameter/third-party/index.vue` — 适配高级模式状态展示
- `src/locales/{en,zh-CN,tw}.ts` — 新增相关 i18n key

**依赖与风险：**
- 依赖已有的 `datasource_drivers.py` 和 `DatasourceService`，无新外部依赖
- 安全风险：`/datasources` 端点返回完整数据库凭据，需确保 API Key 认证安全 + HTTPS 传输
- 凭据提取需处理 `configuration` JSONB 的 key 变体

**Gate layer:** L0（backend ruff + frontend lint）+ L1（backend pytest，15/15 通过）
