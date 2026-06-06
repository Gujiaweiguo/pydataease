## ADDED Requirements

### Requirement: 管理员初始密码 SHALL 通过配置文件指定
管理员初始密码 SHALL 在 `conf/install.env` 中通过 `DE_ADMIN_PASSWORD` 配置，SHALL NOT 硬编码在代码或迁移脚本中。

#### Scenario: 首次安装设置管理员密码
- **WHEN** `install.sh` 执行且 `DE_ADMIN_PASSWORD` 已配置
- **THEN** 安装流程 SHALL 使用该密码创建或更新 admin 用户
- **AND** admin 用户 SHALL 能够使用该密码登录

#### Scenario: 管理员密码为空
- **WHEN** `DE_ADMIN_PASSWORD` 为空
- **THEN** `install.sh` SHALL 报错并中止安装
- **AND** SHALL NOT 创建默认密码的 admin 用户

### Requirement: 管理员密码初始化 SHALL 通过应用内部 CLI 命令执行
管理员密码初始化 SHALL 通过 Python CLI 命令 `python -m app.commands.init_admin` 执行，SHALL NOT 通过 HTTP API 设置。

#### Scenario: CLI 命令执行初始化
- **WHEN** `install.sh` 通过 `docker compose run --rm -e DE_ADMIN_PASSWORD=xxx app python -m app.commands.init_admin` 执行
- **THEN** 命令 SHALL 检查 admin 用户是否存在
- **AND** 如果 admin 不存在 SHALL 创建 admin 用户，密码为 `DE_ADMIN_PASSWORD` 指定的值
- **AND** 如果 admin 已存在 SHALL 跳过（幂等）

#### Scenario: CLI 命令在容器外执行
- **WHEN** CLI 命令在非容器环境（本地开发）中执行
- **THEN** 命令 SHALL 正常工作，读取环境变量 `DE_ADMIN_PASSWORD` 和数据库连接配置

### Requirement: 管理员密码初始化 SHALL 是幂等操作
多次执行初始化命令 SHALL NOT 重复创建 admin 用户或覆盖已修改的密码。

#### Scenario: 重复执行初始化
- **WHEN** `init_admin` 命令被执行且 admin 用户已存在
- **THEN** 命令 SHALL 输出"admin 用户已存在，跳过"并成功退出
- **AND** SHALL NOT 修改现有 admin 用户的密码
