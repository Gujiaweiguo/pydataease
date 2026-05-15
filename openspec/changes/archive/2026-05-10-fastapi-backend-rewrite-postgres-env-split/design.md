## Overview

本设计文档直接派生自 `.sisyphus/plans/fastapi-backend-rewrite-plan-v1.md`，不引入第二套独立计划。设计目标是把 Plan v1 中已经冻结的范围、兼容矩阵、执行波次和技术路径转换为 OpenSpec 可执行上下文，供后续 `/openspec-apply-change`、Atlas 与 Hephaestus 使用。

## Source of Truth

- 唯一规划原稿：`.sisyphus/plans/fastapi-backend-rewrite-plan-v1.md`
- OpenSpec change 仅承载：
  - proposal：为什么做
  - design：如何解释已冻结的技术路径
  - specs：系统应做什么
  - tasks：如何按既有任务编号执行

任何范围、依赖、验收、回滚的修订都必须先回到 Plan v1，再同步到该 change，不并行维护另一套独立计划。

## Scope Baseline

- In scope:
  - Java 后台到 FastAPI 的迁移执行路径
  - uv 管理 Python 环境与依赖
  - PostgreSQL 替代 MySQL/H2 主路径
  - 开发/生产双环境拓扑
  - 认证、中间件、后台任务、安装部署、切换回滚
- Default exclusions for first delivery:
  - desktop/H2
  - distributed/Nacos
  - 未经备案的 xpack 全量等价迁移

## Architecture Direction

### Backend structure

- 新后端采用 FastAPI 模块化结构，建议分层为：
  - `app/main.py`
  - `app/routers/`
  - `app/schemas/`
  - `app/models/`
  - `app/services/`
  - `app/repositories/`
  - `app/middleware/`
  - `app/dependencies/`
  - `app/settings/`
  - `app/tasks/`
- Python 项目通过 `pyproject.toml` + `uv.lock` 管理，不使用裸 `pip` 作为正式路径。

### Contract preservation

- HTTP 契约基线来自：
  - `sdk/api/**/*Api.java`
  - `core/core-frontend/src/api/*.ts`
- 必须优先保留：
  - URL 路径
  - 请求方法
  - 核心 payload 结构
  - 401/403 与错误包装语义
  - `X-DE-TOKEN` / `X-DE-LINK-TOKEN` / `X-EMBEDDED-TOKEN`

### Data platform

- 数据库统一到 PostgreSQL。
- ORM/迁移统一到 SQLAlchemy 2.x async + Alembic。
- 不允许直接搬运 MySQL DDL；需显式处理：
  - unsigned / auto increment
  - JSON 字段
  - 时间戳语义
  - 索引与唯一约束
  - 大小写与布尔差异

### Runtime topology

- 开发环境：本地前端 + 本地 FastAPI + Docker PostgreSQL
- 生产环境：Docker `pydataease-app` + `pydataease-pg`
- 允许保留必要附属组件，但不新增与目标无关的新基础设施。

### Background execution

- 现有 Quartz / sync-task-actuator 必须迁移为 Python 可观测执行链路。
- 任务执行不能全部塞回 Web 进程；需采用 scheduler + worker 或等价隔离方案。

## Execution Sequencing

沿用 Plan v1 的关键路径，不重写编号：

`T01 → T02 → T03 → T04/T05/T06 → T07/T08/T09/T10 → T11/T12 → T13 → F1-F4`

其中：
- Wave 1：范围定格、契约清点、骨架初始化
- Wave 2：数据平台、配置环境、认证中间件
- Wave 3：业务切片迁移
- Wave 4：后台任务、部署链路、切换预演

## Verification Model

- 采用 characterization-first TDD。
- 自动化验证优先级：
  1. contract tests
  2. integration tests
  3. environment/runtime checks
  4. UI smoke
- 所有执行证据归档到 `.sisyphus/evidence/`。

## Risks and controls

- Scope drift → 通过 `migration-scope-governance` capability 与 T01 控制
- API/auth breakage → 通过 characterization tests 与兼容规范控制
- DB migration mismatch → 通过 PostgreSQL/Alembic 规范与演练控制
- Deploy/cutover failure → 通过 runtime-deployment-cutover 规范与 T12/T13 演练控制
