## ADDED Requirements

### Requirement: install.sh SHALL 执行完整的安装流程
`install.sh` SHALL 按顺序执行环境检查、目录创建、镜像加载、配置生成、数据库初始化、应用启动和安装验证。

#### Scenario: 完整安装流程
- **WHEN** 部署人员执行 `./install.sh` 且 `conf/install.env` 已正确配置
- **THEN** 脚本 SHALL 按顺序执行：环境检查 → 创建目录 → 加载镜像 → 生成 docker-compose.yml → 启动 PG（builtin）或验证外部 PG → 执行 Alembic 迁移 → 初始化管理员密码 → 启动 app + nginx → 健康检查 → 写入版本文件 → 输出安装结果

#### Scenario: 必填配置缺失
- **WHEN** `conf/install.env` 中 `DE_SECRET_KEY` 为空
- **THEN** `install.sh` SHALL 在执行任何操作前报告错误并退出
- **AND** SHALL NOT 创建任何容器或修改任何文件

#### Scenario: 端口被占用
- **WHEN** `DE_PORT` 指定的端口已被其他进程占用
- **THEN** `install.sh` SHALL 报告端口冲突并退出

### Requirement: install.sh 和 upgrade.sh SHALL 执行系统环境检查
安装和升级时 SHALL 检查目标系统是否满足运行要求。

#### Scenario: Docker 版本检查
- **WHEN** 系统 Docker Engine 版本低于 24.0
- **THEN** 脚本 SHALL 报告 Docker 版本不满足要求并退出

#### Scenario: Docker Compose v2 检查
- **WHEN** 系统 `docker compose` 命令不可用（仅有旧版 `docker-compose`）
- **THEN** 脚本 SHALL 报告缺少 Docker Compose v2 并退出

#### Scenario: 磁盘空间检查
- **WHEN** 安装目录所在磁盘剩余空间不足 10GB
- **THEN** 脚本 SHALL 报告磁盘空间不足并退出

#### Scenario: 内存检查
- **WHEN** 系统可用内存低于 4GB
- **THEN** 脚本 SHALL 输出警告但继续执行

#### Scenario: 操作系统检查
- **WHEN** 目标系统不是 Ubuntu 22.04 或更高版本
- **THEN** 脚本 SHALL 输出警告但继续执行

### Requirement: start.sh SHALL 启动已安装的服务
`start.sh` SHALL 启动所有容器并等待健康检查通过。

#### Scenario: 正常启动
- **WHEN** 部署人员执行 `./start.sh` 且系统已安装
- **THEN** 脚本 SHALL 执行 `docker compose up -d`
- **AND** SHALL 轮询 `/health` 端点直到返回 200 或超时

#### Scenario: 未安装时启动
- **WHEN** 部署人员执行 `./start.sh` 但 `release/VERSION` 不存在
- **THEN** 脚本 SHALL 提示"系统未安装，请先执行 install.sh"并退出

### Requirement: stop.sh SHALL 停止运行中的服务
`stop.sh` SHALL 优雅停止所有容器。

#### Scenario: 正常停止
- **WHEN** 部署人员执行 `./stop.sh` 且服务正在运行
- **THEN** 脚本 SHALL 执行 `docker compose stop`
- **AND** SHALL 等待容器完全停止

#### Scenario: 服务未运行时停止
- **WHEN** 部署人员执行 `./stop.sh` 但服务未运行
- **THEN** 脚本 SHALL 输出"服务未运行"并正常退出

### Requirement: upgrade.sh SHALL 执行安全的升级流程
`upgrade.sh` SHALL 在升级前自动备份数据库，执行迁移后验证服务健康。

#### Scenario: 完整升级流程
- **WHEN** 部署人员执行 `./upgrade.sh` 并提供新版本镜像
- **THEN** 脚本 SHALL 按顺序执行：环境检查 → 读取当前版本 → 备份数据库 → 加载新镜像 → 停止 app + nginx → 执行 Alembic 迁移 → 启动新容器 → 健康检查 → 更新版本文件

#### Scenario: 迁移失败回滚
- **WHEN** Alembic 迁移执行失败（非零退出码）
- **THEN** 脚本 SHALL 从备份恢复数据库
- **AND** SHALL 启动旧版本容器
- **AND** SHALL 输出回滚成功的提示

#### Scenario: 健康检查失败回滚
- **WHEN** 新版本容器启动后健康检查超时
- **THEN** 脚本 SHALL 回滚 app 和 nginx 容器到旧版本镜像
- **AND** SHALL 输出回滚提示并建议人工检查

#### Scenario: 外部 PG 模式下的备份
- **WHEN** `DE_PG_MODE=external` 且执行升级
- **THEN** 脚本 SHALL 提示部署人员手动备份外部数据库
- **AND** SHALL 等待用户确认后继续升级

### Requirement: uninstall.sh SHALL 清理已安装的系统
`uninstall.sh` SHALL 停止容器并可选删除持久化数据。

#### Scenario: 保留数据的卸载
- **WHEN** 部署人员执行 `./uninstall.sh` 且选择保留数据
- **THEN** 脚本 SHALL 停止并移除所有容器
- **AND** SHALL 保留 `data/`、`conf/`、`release/` 目录

#### Scenario: 完全卸载
- **WHEN** 部署人员执行 `./uninstall.sh --purge`
- **THEN** 脚本 SHALL 停止并移除所有容器
- **AND** SHALL 删除整个安装目录（`DE_INSTALL_DIR`）
- **AND** SHALL 删除 Docker 镜像

#### Scenario: 卸载前确认
- **WHEN** 部署人员执行 `./uninstall.sh`
- **THEN** 脚本 SHALL 在执行任何删除操作前要求用户确认

### Requirement: status.sh SHALL 显示系统运行状态
`status.sh` SHALL 显示各容器的运行状态、版本信息和健康检查结果。

#### Scenario: 显示系统状态
- **WHEN** 部署人员执行 `./status.sh`
- **THEN** 脚本 SHALL 显示：已安装版本、各容器运行状态（running/stopped）、健康检查结果、端口监听状态

### Requirement: 管理脚本 SHALL 通过共享函数库避免代码重复
所有管理脚本 SHALL 通过 `source` 加载 `lib/` 下的共享函数，不重复实现通用逻辑。

#### Scenario: 共享函数加载
- **WHEN** 任意管理脚本启动
- **THEN** 脚本 SHALL 加载 `lib/common.sh`（日志、错误处理、配置读取）
- **AND** 按需加载 `lib/checks.sh`、`lib/docker.sh`、`lib/backup.sh`

#### Scenario: 统一日志格式
- **WHEN** 任意管理脚本输出日志
- **THEN** 日志 SHALL 包含时间戳、日志级别（INFO/WARN/ERROR）和消息内容
- **AND** 日志 SHALL 同时输出到终端和 `logs/scripts/` 目录
