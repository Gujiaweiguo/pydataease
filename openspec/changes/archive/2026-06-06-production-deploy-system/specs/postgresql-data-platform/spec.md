## MODIFIED Requirements

### Requirement: 内置 PostgreSQL SHALL 使用 pgvector 镜像
内置 PostgreSQL 容器 SHALL 使用 `pgvector/pgvector:pg16` 镜像，与开发环境保持一致，支持 vector 扩展。

#### Scenario: 内置 PG 镜像版本
- **WHEN** `DE_PG_MODE=builtin`
- **THEN** `docker-compose.yml` 中 PG 服务 SHALL 使用 `pgvector/pgvector:pg16` 镜像
- **AND** SHALL NOT 使用 `postgres:16` 镜像

#### Scenario: vector 扩展可用
- **WHEN** 内置 PG 容器启动完成
- **THEN** 数据库 SHALL 支持 `CREATE EXTENSION IF NOT EXISTS vector`

### Requirement: 部署 SHALL 支持外部 PostgreSQL 实例
系统 SHALL 支持连接已有的外部 PostgreSQL 实例作为元数据库，不启动内置 PG 容器。

#### Scenario: 使用外部 PG 连接
- **WHEN** `DE_PG_MODE=external` 且 `DE_DATABASE_HOST`、`DE_DATABASE_PORT`、`DE_DATABASE_NAME`、`DE_DATABASE_USER`、`DE_DATABASE_PASSWORD` 已配置
- **THEN** App 容器 SHALL 通过 `DE_DATABASE_URL` 连接外部 PostgreSQL
- **AND** SHALL NOT 启动 `pydataease-pg` 容器

#### Scenario: 外部 PG 连通性验证
- **WHEN** `install.sh` 执行且 `DE_PG_MODE=external`
- **THEN** 脚本 SHALL 测试与外部 PG 的 TCP 连通性
- **AND** SHALL 验证数据库登录成功
- **AND** SHALL 验证 PostgreSQL 版本 >= 14
- **AND** 任一验证失败 SHALL 中止安装

#### Scenario: 外部 PG 自动初始化
- **WHEN** `DE_PG_MODE=external` 且 `DE_PG_ALLOW_INIT=true`
- **THEN** `install.sh` SHALL 尝试在目标 PG 上创建指定数据库（如不存在）
- **AND** SHALL 尝试创建 `vector` 扩展（如不存在）

#### Scenario: 外部 PG 不自动初始化
- **WHEN** `DE_PG_MODE=external` 且 `DE_PG_ALLOW_INIT=false`（默认）
- **THEN** `install.sh` SHALL NOT 在外部 PG 上创建数据库或扩展
- **AND** SHALL 仅验证指定的数据库已存在且可连接
