## 1. 版本管理统一

- [x] 1.1 将 `core/pydataease-backend/app/settings/defaults.py` 中 `about.version` 的硬编码值改为从 `DE_APP_VERSION` 环境变量读取（fallback "2.10"）
- [x] 1.2 修改根目录 `Dockerfile`，添加 `ARG VERSION` 和 `RUN echo $VERSION > /app/VERSION`，在构建时注入版本号
- [x] 1.3 修改 `core/pydataease-backend/app/settings/config.py` 的 `BaseConfig`，添加 `app_version` 字段用于读取 `DE_APP_VERSION`

## 2. 管理员密码初始化 CLI

- [x] 2.1 创建 `core/pydataease-backend/app/commands/__init__.py`（空文件）
- [x] 2.2 创建 `core/pydataease-backend/app/commands/init_admin.py`，实现 `init_admin` CLI 命令：读取 `DE_ADMIN_PASSWORD` 环境变量，检查 admin 用户是否存在，不存在则创建，已存在则跳过（幂等）
- [x] 2.3 在 `core/pydataease-backend/app/settings/config.py` 中添加 `admin_password` 配置项（从 `DE_ADMIN_PASSWORD` 读取）
- [x] 2.4 为 `init_admin` 命令编写单元测试（`tests/test_init_admin.py`）：覆盖新建 admin、admin 已存在、密码为空报错、纯空白密码报错四个场景
- [x] 2.5 验证：`uv run pytest tests/test_init_admin.py -v` 通过（4 passed）

## 3. Nginx 前端容器

- [x] 3.1 创建 `Dockerfile.nginx`（项目根目录），实现多阶段构建：Stage 1 用 `node:18-slim` 构建前端，Stage 2 用 `nginx:stable-alpine` serve 静态文件
- [x] 3.2 创建 `conf/nginx/default.conf`，配置 Nginx：`/` serve 前端静态文件（Vue Router history fallback），`/de2api/` 反向代理到 `pydataease-app:8000`，`/websocket` WebSocket 代理
- [x] 3.3 验证前端构建产物路径：确认 `npm run build:distributed` 的输出目录为 `dist/`（Vite 默认），`Dockerfile.nginx` COPY 路径正确
- [x] 3.4 验证：`docker build -f Dockerfile.nginx -t pydataease-nginx:ci .` 构建成功（125MB）

## 4. Docker Compose 重写

- [x] 4.1 创建 `conf/docker-compose.yml.template`，支持变量替换（`DE_INSTALL_DIR`、`DE_PORT`、`DE_PG_PASSWORD`、`DE_SECRET_KEY` 等），用 `PG_BUILTIN_START/END` 标记让脚本处理条件
- [x] 4.2 模板中 PG 服务使用 `pgvector/pgvector:pg16` 镜像，App 服务使用 `pydataease-app` 镜像，Nginx 服务使用 `pydataease-nginx` 镜像
- [x] 4.3 模板中所有 volumes 使用 bind mount 到 `${DE_INSTALL_DIR}` 下的子目录
- [x] 4.4 同步更新 `core/pydataease-backend/docker-compose.prod.yml` 和根目录 `docker-compose.prod.yml`（3 容器 + pgvector 镜像 + Nginx）
- [x] 4.5 修改 `core/pydataease-backend/scripts/entrypoint.sh`，移除 `alembic upgrade head`，仅保留 uvicorn 启动和信号处理
- [x] 4.6 验证：用测试配置值 `envsubst` 生成 `docker-compose.yml`，`docker compose config` 验证语法正确

## 5. 配置文件模板

- [x] 5.1 创建 `conf/install.env.example`，包含所有配置项和分组注释（安装目录、端口、安全密钥、管理员账号、数据库模式、可选功能）
- [x] 5.2 更新 `core/pydataease-backend/.env.example`，添加 `DE_ADMIN_PASSWORD`、`DE_PG_MODE` 等新增配置项
- [x] 5.3 更新 `core/pydataease-backend/app/settings/config.py`，在 `BaseConfig` 中添加 `pg_mode`、`admin_password`、`install_dir` 等新字段

## 6. 共享函数库（lib/）

- [x] 6.1 创建 `lib/common.sh`：日志函数（带时间戳和级别）、颜色输出、错误处理（`set -euo pipefail`）、`load_env` 函数（读取 `conf/install.env`）
- [x] 6.2 创建 `lib/checks.sh`：`check_os`（Ubuntu 22.04+）、`check_docker`（Docker >= 24）、`check_compose_v2`、`check_disk`（>= 10GB）、`check_memory`（>= 4GB，仅警告）、`check_port`（端口占用）、`check_install_dir`（目录可写）
- [x] 6.3 创建 `lib/docker.sh`：`compose_up`、`compose_stop`、`compose_down`、`wait_for_health`（轮询 `/health`）、`load_images`（离线 docker load / 在线 docker pull）、`run_oneoff`（一次性容器执行命令）
- [x] 6.4 创建 `lib/backup.sh`：`backup_database`（pg_dump 压缩到 `data/backups/`）、`restore_database`（从备份恢复）、`list_backups`

## 7. 管理脚本

- [x] 7.1 创建 `install.sh`：完整安装流程 — 加载配置 → 环境检查 → 创建目录 → 加载镜像 → 生成 docker-compose.yml → 启动 PG（builtin）或验证外部 PG → Alembic 迁移（一次性容器）→ init_admin（一次性容器）→ 启动 app + nginx → 健康检查 → 写入 `release/VERSION` → 输出安装结果
- [x] 7.2 创建 `start.sh`：检查已安装 → `compose_up` → 等待健康检查 → 输出访问地址
- [x] 7.3 创建 `stop.sh`：`compose_stop` → 确认容器已停止
- [x] 7.4 创建 `upgrade.sh`：环境检查 → 读取当前版本 → 备份数据库（builtin）或提示手动备份（external）→ 加载新镜像 → 停止 app + nginx → Alembic 迁移（新镜像一次性容器）→ 启动新容器 → 健康检查 → 更新 `release/VERSION` → 失败回滚（恢复备份 + 旧镜像重启）
- [x] 7.5 创建 `uninstall.sh`：用户确认 → 停止容器 → 移除容器 → `--purge` 时删除安装目录和镜像
- [x] 7.6 创建 `status.sh`：显示已安装版本、各容器运行状态、健康检查结果、端口监听状态

## 8. 外部 PostgreSQL 支持

- [x] 8.1 在 `lib/checks.sh` 中添加 `check_external_pg` 函数：TCP 连通性测试、PostgreSQL 版本验证（>= 14）、登录验证
- [x] 8.2 在 `lib/checks.sh` 中添加 `init_external_pg` 函数（`DE_PG_ALLOW_INIT=true` 时）：创建数据库、创建 vector 扩展
- [x] 8.3 更新 `core/pydataease-backend/app/settings/config.py`，添加 `database_host`、`database_port`、`database_name`、`database_user`、`database_password`、`database_sslmode`、`pg_allow_init` 等配置项

## 9. 验证与测试

- [x] 9.1 后端验证：`cd core/pydataease-backend && uv run ruff check .` 通过
- [x] 9.2 后端测试：`cd core/pydataease-backend && uv run pytest tests/test_init_admin.py -v` 通过（4 passed）
- [x] 9.3 后端 Docker 构建：`docker build -t pydataease-backend:ci .` 成功（VERSION 注入验证通过）
- [x] 9.4 Nginx Docker 构建：`docker build -f Dockerfile.nginx -t pydataease-nginx:ci .` 成功（采用预构建模式，前端需先本地 `npm run build:distributed`）
- [x] 9.5 前端构建验证：`cd core/core-frontend && npm run build:distributed` 成功（本地已验证）
- [x] 9.6 Shell 脚本语法检查：所有 10 个脚本 `bash -n` 语法验证通过（shellcheck 未安装，跳过）
- [ ] 9.7 端到端冒烟测试（需要运行环境）：`install.sh` 全流程执行成功，`status.sh` 显示所有容器 healthy，浏览器访问 `http://localhost:8100` 返回前端页面，`/de2api/health` 返回 200