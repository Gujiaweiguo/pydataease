## Context

PyDataEase 当前集成 MySQLBot 使用**基础小助手模式**（type=0）：
- 后端有 4 个 stub 端点（`/sysParameter/sqlbot` GET/POST、`/sqlbot/datasource`、`/sqlbot/dataset/{dv_info}`），均返回空数组或仅读写设置
- 前端通过 `assistant.js`（浮动窗口）和 `sqlbot-embedded-dynamic.umd.js`（全屏）加载 MySQLBot 的 JS bundle
- MySQLBot 侧自行管理所有数据源、AI 模型、SQL 生成——pydataease 只提供"宿主容器"

**高级小助手模式**（type=1）是 MySQLBot 的另一种集成方式，MySQLBot 不直接管理数据源，而是通过管理员配置的 **endpoint URL** 回调第三方系统获取数据源信息。MySQLBot 在请求时会携带接口凭证（通过 header/cookie/param），第三方系统验证凭证后返回数据。

### 关键发现：MySQLBot 高级小助手的实际回调机制

通过分析 MySQLBot 源码（`/opt/code/mysqlbot/backend/apps/system/crud/assistant.py`），确认高级小助手的实际工作流程：

1. **MySQLBot 只调用一个端点**——管理员配置的 `endpoint`（通常是 `GET /datasources`），不是多个端点
2. **该端点必须返回完整的数据库连接凭据**——每个数据源包含 `host`、`port`、`user`、`password`、`dataBase` 等字段
3. **MySQLBot 拿到凭据后直连数据库**——它不会回调 pydataease 执行 SQL，而是用自己的驱动连接数据库
4. 响应格式必须匹配 MySQLBot 的 `AssistantOutDsSchema`（`id`、`name`、`type`、`host`、`port`、`dataBase`、`user`、`password`、`extraParams`、`db_schema` 等）

这意味着 pydataease 不是 SQL 代理，而是**数据源凭据提供者**。

**当前基础设施（可直接复用）：**
- `SysSettingService`：`get_sqlbot_settings()` / `save_sqlbot_settings()` 已有 sqlbot.* 配置读写
- 中间件 `AuthMiddleware` + `whitelist.py`：已有完整的认证/白名单机制
- `ResultMessageMiddleware`：自动包装 `{code, data, msg}` 响应格式，MySQLBot 检查 `code == 0 or code == 200`
- `DatasourceRepository`：查询 `core_datasource` 表，`configuration` JSONB 字段存储连接凭据

## Goals / Non-Goals

**Goals:**
- 提供一个 REST API 端点供 MySQLBot 高级小助手回调，返回数据源列表及其连接凭据
- 响应格式严格匹配 MySQLBot 的 `AssistantOutDsSchema`，使 MySQLBot 能直接连接数据库
- 使用 API Key 认证（独立于 pydataease 的 JWT），与 MySQLBot 高级小助手的接口凭证机制对齐
- 保留额外的 tables/fields/query 端点作为通用数据库元数据 API（虽然 MySQLBot 当前不使用）
- 在前端系统设置中支持配置高级小助手模式（endpoint、API Key）
- 保持与现有基础小助手模式的向后兼容

**Non-Goals:**
- 不修改 MySQLBot 本身的代码——这是 pydataease 单侧变更
- 不实现 SSE/流式响应——MySQLBot 高级小助手当前使用同步 REST 回调
- 不实现 AES 加密——MySQLBot 侧可选的 AES 用于数据源字段加密，pydataease 作为数据提供方无需处理
- 不实现 MySQLBot 的工作空间映射——pydataease 侧按 API Key 粒度控制数据源范围
- 不修改现有基础小助手模式的任何行为

## Decisions

### D1: API 路径前缀使用 `/mysqlbot/api/` 而非 `/sqlbot/`

**选择**: 新端点挂载在 `/de2api/mysqlbot/api/` 下

**理由**: 现有 `/de2api/sqlbot/` 路径已被基础小助手 stub 端点使用。使用独立前缀清晰区分两种模式，避免路径冲突，也方便白名单管理。

**替代方案**: 复用 `/sqlbot/` 前缀 + 查询参数区分 → 拒绝，因为语义不清，且 stub 端点和功能端点混在一起难以维护。

### D2: 认证方案使用 API Key + 白名单豁免

**选择**: `/mysqlbot/api/` 路径加入 `WHITE_PREFIXES` 白名单，跳过 JWT AuthMiddleware。在路由层通过自定义 `Depends(verify_mysqlbot_api_key)` 依赖验证 `X-API-Key` header。

**理由**: MySQLBot 高级小助手不支持 pydataease 的 JWT 认证——它通过管理员配置的接口凭证发起请求。使用独立的 API Key 机制最简单、最解耦。

**替代方案**:
- 在 AuthMiddleware 中新增 token 类型 → 拒绝，修改全局中间件风险太大
- 使用 Basic Auth → 拒绝，MySQLBot 高级小助手的凭证机制已经支持 header/cookie/param，API Key 最匹配

### D3: 数据源端点返回完整连接凭据

**选择**: `GET /mysqlbot/api/datasources` 返回每个数据源的完整连接凭据（`host`、`port`、`user`、`password`、`dataBase`），从 `core_datasource.configuration` JSONB 字段提取。

**理由**: MySQLBot 高级小助手的工作机制是获取凭据后直连数据库，不是通过 pydataease 代理执行 SQL。这是 MySQLBot `AssistantOutDs.convert2schema()` 的硬性要求。

**替代方案**: 只返回元数据，让 MySQLBot 通过额外端点查询 → 拒绝，MySQLBot 的 `get_ds_from_api()` 期望一个端点返回所有信息，不支持多步回调。

### D4: API Key 存储在 sys_setting 中

**选择**: 复用已有的 `SysSettingService`，新增 `sqlbot.apiKey` 设置项。API Key 以明文存储（与现有 `sqlbot.domain`、`sqlbot.id` 等设置项一致）。

**理由**: pydataease 的系统设置已经使用这个模式存储各种配置（包括 `DE_SECRET_KEY` 等敏感信息）。API Key 是管理员手动配置的共享密钥，与 MySQLBot 两侧约定一致。后续如需加密存储，可以作为独立改进。

**替代方案**: 使用独立的数据库表存储 API Key → 拒绝，过度设计，当前规模不需要

### D5: 保留 tables/fields/query 端点作为通用 API

**选择**: 虽然MySQLBot 高级小助手当前只调用 datasources 端点，但保留 tables/fields/query 三个端点作为通用数据库元数据查询 API。

**理由**: 这些端点已经实现且测试通过，可能在其他集成场景中有用（如自定义 BI 工具、数据目录查询等）。保留成本为零（只是额外的路由），删除则浪费已完成的实现和测试。

### D6: 数据源范围不过滤

**选择**: 不实现动态的数据源范围过滤。API Key 验证通过后，返回该 pydataease 实例中所有非 folder 类型的数据源。

**理由**: MySQLBot 高级小助手的工作空间/数据源范围配置是 MySQLBot 侧的概念，pydataease 作为数据提供方只需确保返回的数据源是合法可查询的。更精细的范围控制可以作为后续增强。

## Risks / Trade-offs

**[安全风险] 数据库凭据暴露** → API 通过 API Key 认证保护，HTTPS 传输加密。凭据仅返回给通过认证的请求。建议生产环境定期轮换 API Key 和数据库密码。

**[安全风险] API Key 泄露** → API Key 通过 HTTPS 传输（生产环境强制），仅在系统设置页面显示给管理员。日志中过滤 `X-API-Key` header。建议文档中提醒管理员定期轮换 Key。

**[功能限制] 不支持数据源权限过滤** → 当前返回所有可连接的数据源。→ 后续增强：可以增加 `sqlbot.allowedDatasourceIds` 配置项限制返回的数据源范围。

**[Trade-off] 明文存储 API Key** → 接受这个 trade-off，与现有设置存储方式一致。生产环境中 `.env` 中的 `DE_SECRET_KEY` 等也是类似模式。

## Open Questions

(None — all questions resolved during implementation and testing.)
