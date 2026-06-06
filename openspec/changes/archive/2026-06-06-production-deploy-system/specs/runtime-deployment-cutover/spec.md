## MODIFIED Requirements

### Requirement: Docker Compose 生产部署 SHALL 使用 3 容器架构
生产部署 SHALL 使用 Nginx + App + PostgreSQL 三个容器，通过 Docker Compose 编排。

#### Scenario: builtin 模式下的 3 容器部署
- **WHEN** `DE_PG_MODE=builtin`
- **THEN** `docker-compose.yml` SHALL 定义 `pydataease-nginx`、`pydataease-app`、`pydataease-pg` 三个服务
- **AND** `pydataease-nginx` SHALL 依赖 `pydataease-app` 的健康检查
- **AND** `pydataease-app` SHALL 依赖 `pydataease-pg` 的健康检查

#### Scenario: external 模式下的 2 容器部署
- **WHEN** `DE_PG_MODE=external`
- **THEN** `docker-compose.yml` SHALL 只定义 `pydataease-nginx` 和 `pydataease-app` 两个服务
- **AND** `pydataease-app` 的 `DE_DATABASE_URL` SHALL 指向外部 PostgreSQL 地址

### Requirement: 持久化数据 SHALL 使用 bind mount
生产部署 SHALL 使用绑定挂载（bind mount）替代 Docker 命名卷，所有数据存放在 `DE_INSTALL_DIR` 下的固定子目录中。

#### Scenario: 数据目录绑定挂载
- **WHEN** `DE_INSTALL_DIR=/opt/module/pydataease`
- **THEN** `docker-compose.yml` SHALL 将 `${DE_INSTALL_DIR}/data/postgres` 挂载到 PG 容器的 `/var/lib/postgresql/data`
- **AND** 将 `${DE_INSTALL_DIR}/logs/app` 挂载到 App 容器的 `/app/logs`
- **AND** 将 `${DE_INSTALL_DIR}/static` 挂载到 App 容器的 `/app/static`

### Requirement: Docker Compose 配置 SHALL 动态生成
`docker-compose.yml` SHALL 由 `install.sh` 根据配置动态生成，SHALL NOT 硬编码安装路径或数据库连接信息。

#### Scenario: 从模板生成配置
- **WHEN** `install.sh` 执行
- **THEN** SHALL 读取 `conf/docker-compose.yml.template` 模板
- **AND** SHALL 使用 `envsubst` 替换模板中的变量
- **AND** SHALL 将结果写入 `conf/docker-compose.yml`

#### Scenario: 生成的配置验证
- **WHEN** `docker-compose.yml` 生成完毕
- **THEN** `install.sh` SHALL 执行 `docker compose config` 验证语法正确性
- **AND** 验证失败 SHALL 中止安装

### Requirement: entrypoint.sh SHALL 仅启动应用
`entrypoint.sh` SHALL 移除 `alembic upgrade head` 调用，仅负责启动 uvicorn 服务。

#### Scenario: 容器启动不再执行迁移
- **WHEN** App 容器启动
- **THEN** `entrypoint.sh` SHALL 仅执行 `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **AND** SHALL NOT 执行 `alembic upgrade head`
