## Why

DataEase 当前后端深度耦合 Spring Boot、MyBatis-Plus、Quartz、MySQL/H2 与安装脚本，已经与目标的 Python/FastAPI/PostgreSQL 技术方向不一致。现在需要基于唯一 Plan v1 建立一条可执行、可验证、可回滚的正式变更路径，把计划转换为 OpenSpec change，作为后续实现与验收的统一契约。

## What Changes

- 用 FastAPI 重构当前 Java 后台，并以 uv 统一管理 Python 版本、依赖与执行入口。
- **BREAKING**：后端实现栈从 Spring Boot/MyBatis/Quartz/Flyway 迁移到 FastAPI/SQLAlchemy/Alembic/PostgreSQL，但必须保持前端当前关键 HTTP API、认证头语义与核心响应结构兼容。
- 将数据库主路径统一到 PostgreSQL，建立 Alembic schema 初始化与迁移链路。
- 固化两种目标环境：开发环境为本地前端 + 本地 FastAPI + Docker PostgreSQL；生产环境为 Docker `pydataease-app` + `pydataease-pg`。
- 重建认证、中间件、后台任务、部署脚本、切换与回滚流程，并把验证要求纳入正式规范。
- 默认不将 desktop/H2、distributed/Nacos 作为首批必须交付范围；它们若需要进入范围，必须作为受控扩展处理。

## Capabilities

### New Capabilities
- `migration-scope-governance`: 冻结迁移范围、兼容矩阵与非目标项，防止执行期 scope drift。
- `backend-contract-compatibility`: 规定前端现有 API 路径、请求/响应结构与错误行为的兼容要求。
- `auth-runtime-compatibility`: 规定 `X-DE-TOKEN`、`X-DE-LINK-TOKEN`、`X-EMBEDDED-TOKEN`、白名单与响应包装兼容要求。
- `postgresql-data-platform`: 规定 PostgreSQL、SQLAlchemy async、Alembic 与历史数据迁移要求。
- `runtime-deployment-cutover`: 规定开发/生产拓扑、后台任务、安装部署、切换与回滚要求。

### Modified Capabilities
- None.

## Impact

- Affected code: `core/core-backend/**`, `core/core-frontend/src/api/**`, `sdk/api/**`, `sdk/common/**`, `installer/**`, `Dockerfile`, future Python backend directory.
- Affected systems: backend runtime, auth pipeline, database platform, background jobs, installer/deployment topology, verification pipeline.
- Affected dependencies: Java/Spring stack will be replaced by FastAPI, uv, SQLAlchemy async, Alembic, PostgreSQL and related Python tooling.
