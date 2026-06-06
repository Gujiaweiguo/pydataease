## Context

PyDataEase 当前有一个基础的生产 Docker Compose 配置（2 容器：app + postgres:16），但存在以下问题：

1. **前端不在镜像内** — 根目录 Dockerfile 只构建 Python 后端，`/app/static` 是空目录，前端需要单独部署或开发模式运行
2. **配置分散** — 密钥在 `.env`，数据库密码在 Compose 环境变量，管理员密码硬编码在 Alembic 迁移脚本（`DataEase@123456`）
3. **没有生命周期管理** — 无安装、升级、卸载流程，`entrypoint.sh` 每次启动盲跑 `alembic upgrade head`
4. **版本号不统一** — `pyproject.toml` 写 `0.1.0`，`defaults.py` 写 `2.10`，Docker 镜像没有版本标签
5. **持久化用命名卷** — 数据存在 Docker 内部目录，部署人员无法直接管理和备份

目标用户：国内政企环境运维人员，Ubuntu 22.04+ 服务器，可能在内网/离线环境。

## Goals / Non-Goals

**Goals:**

- 提供一个自包含的生产部署包，部署人员编辑一个 `conf/install.env` 文件后执行 `./install.sh` 即可完成安装
- 支持 3 容器架构（Nginx + App + PG），对外只暴露一个 HTTP 端口
- 支持离线安装（`docker save/load` tar 包）和在线安装（`docker pull`）
- 支持外部 PostgreSQL，允许复用已有的数据库实例
- 支持 install / start / stop / upgrade / uninstall / status 全生命周期命令
- 升级时自动备份数据库，迁移失败可回滚
- 管理员初始密码在配置文件中指定，不硬编码
- 所有持久化数据 bind mount 到统一安装目录下

**Non-Goals:**

- 不做 Kubernetes / Helm 部署（本方案只面向 Docker Compose 场景）
- 不做多节点集群、高可用、负载均衡（单机部署）
- 不做蓝绿部署、金丝雀发布（升级采用停机替换）
- 不做自动化的滚动回滚（需要手动触发回滚或恢复备份）
- 不修改后端业务逻辑、API 接口或前端组件代码
- 不做 Windows / macOS 部署支持
- 不做在线管理界面（所有操作通过命令行脚本）

## Decisions

### D1: 3 容器架构 — Nginx + App + PG

**决策**：使用独立的 Nginx 容器 serve 前端静态文件并反向代理后端 API。

**方案**：
```
pydataease-nginx  (nginx:stable-alpine)
  ├─ :80 → /usr/share/nginx/html (前端静态文件)
  ├─ /de2api/* → proxy_pass http://pydataease-app:8000
  └─ /websocket → proxy_pass http://pydataease-app:8000 (WebSocket upgrade)

pydataease-app    (项目构建镜像)
  └─ :8000 → FastAPI (uvicorn)

pydataease-pg     (pgvector/pgvector:pg16, 仅 builtin 模式)
  └─ :5432 → PostgreSQL (仅内部网络)
```

**备选方案**：
- A) 前端打包进后端镜像，用 FastAPI StaticFiles serve — 实现简单但性能差，Nginx 处理静态文件的吞吐量是 Python 的 10 倍以上，且无法独立更新前端
- B) 前端和后端共用一个容器，容器内跑 Nginx + uvicorn（supervisor 管理）— 增加复杂度，违背一个容器一个进程的原则

**理由**：Nginx 独立容器是生产部署的标准实践，性能最优、职责分离、前端可独立更新。

### D2: 前端构建方式 — 多阶段 Dockerfile

**决策**：新增 `Dockerfile.nginx`，多阶段构建：

```dockerfile
# Stage 1: 构建前端
FROM node:18-slim AS frontend-builder
WORKDIR /build
COPY core/core-frontend/package.json core/core-frontend/package-lock.json ./
RUN npm ci
COPY core/core-frontend/ .
RUN npm run build:distributed

# Stage 2: Nginx 运行时
FROM nginx:stable-alpine
COPY --from=frontend-builder /build/dist /usr/share/nginx/html
COPY conf/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

后端镜像保持现有 `Dockerfile` 不变。

**理由**：前后端镜像分离，可以独立构建和版本化。前端构建需要 Node.js 工具链，不应该污染后端镜像。

### D3: 脚本架构 — 多脚本 + 共享函数库

**决策**：6 个独立脚本 + `lib/` 共享函数库。

```
install.sh    → 调用 lib/common.sh + lib/checks.sh + lib/docker.sh
start.sh      → 调用 lib/common.sh + lib/docker.sh
stop.sh       → 调用 lib/common.sh + lib/docker.sh
upgrade.sh    → 调用 lib/common.sh + lib/checks.sh + lib/docker.sh + lib/backup.sh
uninstall.sh  → 调用 lib/common.sh + lib/docker.sh
status.sh     → 调用 lib/common.sh + lib/docker.sh

lib/
├── common.sh    — 日志、颜色输出、错误处理、环境变量加载
├── checks.sh    — 系统环境检查（OS、Docker、磁盘、端口、内存）
├── docker.sh    — Docker Compose 操作封装（启动、停止、健康检查）
└── backup.sh    — 数据库备份/恢复（pg_dump / pg_restore）
```

**备选方案**：单脚本 `pydataease.sh install|start|stop|...`

**理由**：政企运维场景下，SOP 文档通常是"执行 `./install.sh`"这样的步骤，独立脚本更直观。内部共享函数库避免代码重复。不排除未来加一个 `pydataease.sh` 做统一入口，但不是初始版本的必要功能。

### D4: 配置文件 — conf/install.env 为唯一入口

**决策**：所有部署参数集中在 `conf/install.env`，格式为 `KEY=VALUE`，带分组注释。

关键配置项：

```bash
DE_INSTALL_DIR=/opt/module/pydataease  # 安装根目录
DE_PORT=8100                            # 对外端口
DE_SECRET_KEY=                          # [必填] JWT 签名密钥
DE_SHARE_SECRET_KEY=                    # [必填] 分享 Token 密钥
DE_ADMIN_PASSWORD=                      # [必填] 管理员初始密码
DE_PG_MODE=builtin                      # builtin | external
DE_PG_PASSWORD=                         # builtin 模式下 PG 密码
DE_DATABASE_HOST=                       # external 模式下 PG 地址
DE_DATABASE_PORT=5432
DE_DATABASE_NAME=dataease
DE_DATABASE_USER=
DE_DATABASE_PASSWORD=
DE_DATABASE_SSLMODE=prefer
DE_IMAGE_DIR=                           # 离线镜像目录，留空则从 registry 拉取
DE_BACKUP_BEFORE_UPGRADE=true
DE_BACKUP_DIR=                          # 默认 ${DE_INSTALL_DIR}/data/backups
DE_PG_ALLOW_INIT=false                  # 是否允许在外部 PG 上建库建扩展
```

**理由**：`.env` 格式被 Docker Compose 原生支持（`env_file` 指令），也被 Pydantic Settings 原生支持（`env_prefix="DE_"`），不需要额外的解析层。

### D5: 升级流程 — 独立迁移 + 自动备份 + 回滚

**决策**：将 Alembic 迁移从 `entrypoint.sh` 中移出，由 `upgrade.sh` 显式执行。

升级流程：
1. 环境检查（Docker、磁盘、备份目录）
2. 读取 `release/VERSION` 获取当前版本
3. 备份数据库 → `data/backups/{timestamp}.sql.gz`
4. 加载新镜像（`docker load` 或 `docker pull`）
5. 停止 app 和 nginx 容器（PG 保持运行，如果是 builtin 模式）
6. 用新镜像跑一次性迁移容器：`docker compose run --rm app alembic upgrade head`
7. 迁移成功 → 启动新版本容器
8. 轮询 `/health` 直到 200
9. 更新 `release/VERSION`
10. 失败回滚：
    - 迁移失败 → 恢复数据库备份，启动旧版本容器
    - 迁移成功但健康检查失败 → 回滚 app/nginx 容器到旧镜像

**`entrypoint.sh` 改动**：移除 `alembic upgrade head`，仅保留 uvicorn 启动。首次安装的迁移由 `install.sh` 通过一次性容器执行。

**备选方案**：保持 entrypoint 自动迁移（当前做法）

**理由**：显式迁移让升级过程可控、可观测、可回滚。entrypoint 盲跑迁移的问题是：如果迁移失败，容器会不断重启，日志混在应用日志里，运维人员难以定位问题。

### D6: 管理员密码初始化 — 应用内部 CLI 命令

**决策**：新增 `app/commands/init_admin.py`，作为 Python 模块运行。

```bash
# install.sh 内部调用：
docker compose run --rm -e DE_ADMIN_PASSWORD=xxx app \
  python -m app.commands.init_admin
```

命令行为：
- 检查 admin 用户是否存在
- 不存在 → 创建 admin 用户，密码使用 `DE_ADMIN_PASSWORD`
- 已存在 → 跳过（幂等）
- `DE_ADMIN_PASSWORD` 为空 → 报错退出，安装中止

**备选方案**：通过 HTTP API 修改密码

**理由**：CLI 方式不依赖 HTTP 就绪状态，不受反向代理/网络策略影响，可以在数据库就绪后立即执行，比 API 调用更可靠。

### D7: 版本管理 — 统一来源 + 镜像标签 + 本地记录

**决策**：
- 版本号统一从 `pyproject.toml` 的 `project.version` 读取
- Docker 构建时通过 `--build-arg VERSION=x.y.z` 注入，写入 `/app/VERSION` 文件
- 镜像标签格式：`pydataease-app:x.y.z`、`pydataease-nginx:x.y.z`
- 安装目录下 `release/VERSION` 记录已安装版本，`upgrade.sh` 读取并比较

**理由**：`pyproject.toml` 是 Python 项目的标准版本来源，构建时注入确保镜像和代码版本一致。本地 VERSION 文件让脚本可以无依赖地判断当前版本。

### D8: 目录结构

**决策**：
```
${DE_INSTALL_DIR}/
├── bin/                    # 管理脚本
│   ├── install.sh
│   ├── start.sh
│   ├── stop.sh
│   ├── upgrade.sh
│   ├── uninstall.sh
│   ├── status.sh
│   └── lib/
│       ├── common.sh
│       ├── checks.sh
│       ├── docker.sh
│       └── backup.sh
├── conf/
│   ├── install.env         # 部署配置（唯一入口）
│   ├── docker-compose.yml  # 根据配置动态生成
│   └── nginx/
│       └── default.conf    # Nginx 配置模板
├── data/
│   ├── postgres/           # PG 数据（builtin 模式）
│   └── backups/            # 升级前自动备份
├── logs/
│   ├── app/                # 应用日志
│   └── scripts/            # 脚本执行日志
├── static/                 # 静态资源
├── images/                 # 离线镜像 tar 包
└── release/
    └── VERSION             # 已安装版本号
```

**理由**：配置、数据、日志、脚本分离，符合 FHS 惯例。`bin/` 放脚本而非根目录，保持安装目录整洁。`release/VERSION` 作为版本状态文件，独立于业务数据。

### D9: 外部 PostgreSQL 支持

**决策**：

- `DE_PG_MODE=builtin` — 启动 PG 容器，app 通过 Compose 内部网络连接
- `DE_PG_MODE=external` — 不启动 PG 容器，app 通过 `DE_DATABASE_URL` 连接外部实例
- `DE_PG_ALLOW_INIT=false`（默认）— 只验证连通性，不建库建扩展
- `DE_PG_ALLOW_INIT=true` — 自动执行 `CREATE DATABASE`、`CREATE EXTENSION vector`（如果权限允许）

`install.sh` 在 external 模式下的验证步骤：
1. TCP 连通性测试（`nc -z host port`）
2. PostgreSQL 版本检查（要求 >= 14）
3. 登录验证（`psql` 或 Python 脚本）
4. 如果 `DE_PG_ALLOW_INIT=true`，尝试创建数据库和扩展

**理由**：政企环境中数据库通常由 DBA 团队管理，安装脚本不应该假设有超级用户权限。显式的 `DE_PG_ALLOW_INIT` 让部署人员和 DBA 清楚知道脚本会做什么。

### D10: Docker Compose 动态生成

**决策**：`install.sh` 根据配置动态生成 `conf/docker-compose.yml`。

原因：因为 `DE_PG_MODE` 决定是否包含 PG 容器，`DE_INSTALL_DIR` 决定 bind mount 路径，这些不能硬编码在静态 Compose 文件里。方案是在 `conf/` 下维护一个 `docker-compose.yml.template` 模板文件，`install.sh` 用 `envsubst` 替换变量后输出到 `conf/docker-compose.yml`。

**备选方案**：使用 Docker Compose 的 `profiles` 特性区分 builtin/external 模式

**理由**：`envsubst` 方案简单直观，运维人员可以直接看生成的 `docker-compose.yml` 理解最终配置。`profiles` 特性增加了学习成本，且无法处理 bind mount 路径的动态替换。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|---|---|
| 前端构建增加 Docker build 时间和镜像体积 | Node.js 构建只在 builder 阶段，不影响运行时镜像大小；Nginx alpine 镜像约 25MB |
| 升级时停机时间不可控 | 对于单机部署场景可接受；未来如需零停机需引入蓝绿部署，属于 Non-Goal |
| `envsubst` 生成 Compose 文件可能引入语法错误 | 生成后用 `docker compose config` 验证，验证失败中止安装 |
| 外部 PG 环境下，升级前的数据库备份依赖外部工具 | `upgrade.sh` 检测到 external 模式时提示部署人员手动备份，不自动执行 pg_dump |
| Shell 脚本在非 Ubuntu 发行版上可能有兼容性问题 | 系统检查时检测 OS 版本，非 Ubuntu 22.04+ 给出警告；脚本严格使用 POSIX 兼容语法 |
| 管理员密码通过环境变量传递，可能出现在进程列表中 | 一次性容器执行后立即退出；未来可支持 `DE_ADMIN_PASSWORD_FILE` 从文件读取 |
| Alembic 迁移无法真正回滚（只有 upgrade 没有 downgrade 脚本） | 回滚策略依赖数据库备份恢复，而非 Alembic downgrade |

## Migration Plan

### 安装流程（install.sh）

1. 系统环境检查（OS、Docker、磁盘、端口）
2. 加载镜像（`docker load` 离线 / `docker pull` 在线）
3. 创建目录结构（`data/`、`logs/`、`conf/`、`static/`、`release/`）
4. 复制管理脚本到 `bin/`
5. 生成 `conf/docker-compose.yml`（从模板 + install.env）
6. 验证配置（`docker compose config`）
7. 启动 PG 容器（builtin 模式）或验证外部 PG 连通性
8. 执行 Alembic 迁移（一次性容器）
9. 初始化管理员密码（一次性容器）
10. 启动 app + nginx 容器
11. 健康检查轮询 `/health`
12. 写入 `release/VERSION`
13. 输出安装结果（访问地址、管理员账号）

### 升级流程（upgrade.sh）

1. 系统环境检查
2. 读取当前版本
3. 备份数据库
4. 加载新镜像
5. 停止 app + nginx 容器
6. 执行 Alembic 迁移（新镜像一次性容器）
7. 启动新版本容器
8. 健康检查
9. 更新 `release/VERSION`
10. 失败时从备份恢复

### 回滚策略

- **迁移失败**：恢复数据库备份，重启旧版本容器
- **健康检查失败**：回滚 app/nginx 容器到旧镜像
- 回滚操作需要旧版本镜像仍存在于本机（`upgrade.sh` 不删除旧镜像）

## Open Questions

1. **Nginx WebSocket 配置**：当前后端 WebSocket 端点 `/websocket` 是兼容性 stub，Nginx 反向代理 WebSocket 需要额外的 `Upgrade` 头配置。需要确认这个端点是否在生产环境中真正使用。
2. **前端构建产物位置**：`core/core-frontend/` 的 `npm run build:distributed` 输出目录需要确认（可能是 `dist/`），以确保 Dockerfile.nginx 正确 COPY。
3. **离线镜像打包脚本**：是否需要在项目中新增一个 `build-release.sh` 脚本，用于在构建服务器上一键构建所有镜像并导出 tar 包？这不在当前 change 范围内，但与离线安装流程紧密相关。
