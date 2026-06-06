## Why

当前项目没有生产级部署方案：配置分散在多个文件中，管理员密码硬编码在迁移脚本里，Docker 镜像不含前端资源，没有安装/升级/卸载流程。部署人员需要自行理解 `.env`、`docker-compose.prod.yml`、Alembic 迁移、Nginx 配置等多个子系统才能上线，门槛高且容易出错。需要一套开箱即用的生产部署包：修改一个配置文件、执行一条命令即可完成全生命周期管理。

## What Changes

- **新增 Nginx 容器**：前端构建产物由 Nginx serve，`/de2api/` 和 `/websocket` 反向代理到后端。生产环境从 2 容器扩展到 3 容器（Nginx + App + PG）
- **新增前端构建流程**：Dockerfile 新增 Node.js 构建阶段，将前端产物输出给 Nginx 容器
- **PG 镜像升级**：从 `postgres:16` 切换到 `pgvector/pgvector:pg16`，与开发环境一致，支持向量扩展复用
- **新增部署管理脚本体系**：`install.sh`、`start.sh`、`stop.sh`、`upgrade.sh`、`uninstall.sh`、`status.sh`，内部共享 `lib/` 函数库
- **新增统一配置文件** `conf/install.env`：所有部署参数（安装目录、端口、密钥、数据库模式、管理员账号）集中在一个文件中，部署人员修改后再安装
- **支持外部 PostgreSQL**：`DE_PG_MODE=builtin|external`，external 模式下不启动内置 PG 容器，连接已有数据库实例
- **支持离线安装**：`images/` 目录放置 `docker save` 导出的镜像 tar 包，`install.sh` 通过 `docker load` 加载，无需外网
- **管理员密码可配置化**：不再硬编码 `DataEase@123456`，新增应用内部初始化命令，安装时通过 `DE_ADMIN_PASSWORD` 设置
- **持久化数据 bind mount**：从 Docker 命名卷改为绑定挂载到 `DE_INSTALL_DIR`（默认 `/opt/module/pydataease/`）下的固定目录结构，便于备份和统一管理
- **升级流程增强**：升级前自动备份数据库、独立执行 Alembic 迁移（不再依赖 entrypoint 盲跑）、健康检查失败自动回滚
- **系统环境检查**：install 和 upgrade 时自动检查 Ubuntu 22.04+、Docker 版本、磁盘空间、端口占用等
- **版本管理**：统一项目版本号来源，Docker 镜像注入版本标签，安装目录记录已安装版本

## Capabilities

### New Capabilities

- `production-deploy-package`: 生产部署包——包含容器镜像、管理脚本、配置模板的完整分发包，支持离线安装、全生命周期管理（安装/启动/停止/升级/卸载/状态查询）
- `nginx-frontend-serving`: Nginx 容器作为前端静态资源和 API 反向代理层，Dockerfile 多阶段构建包含前端编译
- `deploy-lifecycle-scripts`: 部署管理脚本体系（install/start/stop/upgrade/uninstall/status）及共享函数库（环境检查、备份、Docker 操作）
- `admin-password-init`: 管理员初始密码通过配置文件指定，应用内部 CLI 命令执行初始化，替代迁移脚本硬编码密码

### Modified Capabilities

- `runtime-deployment-cutover`: docker-compose.prod.yml 重写——3 容器架构、bind mount、PG 镜像升级、外部 PG 支持
- `postgresql-data-platform`: 元数据库从 `postgres:16` 切换到 `pgvector/pgvector:pg16`，新增外部 PG 连接模式

## Impact

**新增文件**：
- `install.sh`、`start.sh`、`stop.sh`、`upgrade.sh`、`uninstall.sh`、`status.sh`
- `lib/common.sh`、`lib/checks.sh`、`lib/docker.sh`、`lib/backup.sh`
- `conf/install.env.example`（配置模板）
- `conf/nginx/default.conf`（Nginx 配置）
- `Dockerfile.nginx`（前端 + Nginx 构建镜像）
- `app/commands/init_admin.py`（管理员初始化 CLI 命令）

**修改文件**：
- `docker-compose.prod.yml` — 重写为 3 容器 + bind mount + 外部 PG 支持
- `core/pydataease-backend/scripts/entrypoint.sh` — 移除自动迁移，仅启动 uvicorn
- `app/settings/config.py` — 新增 `DE_ADMIN_PASSWORD`、`DE_PG_MODE` 等配置项

**不改动**：
- 后端业务逻辑、API 接口、前端组件代码均不受影响
- Alembic 迁移文件不变，只是调用时机从 entrypoint 移到 upgrade.sh

**测试层级**：此变更属于 Release/打包类，需要 L0 + L2（Docker 构建验证）+ L3（完整安装流程验证）
