## ADDED Requirements

### Requirement: 生产部署包 SHALL 包含完整的运行时组件
生产部署包 SHALL 包含应用后端镜像、Nginx 前端镜像、数据库镜像（builtin 模式）、管理脚本、配置模板和 Nginx 配置，作为一个自包含的分发单元。

#### Scenario: 离线安装包内容完整
- **WHEN** 部署人员将部署包复制到生产服务器并解压
- **THEN** 包内 SHALL 包含 `images/` 目录下的所有 Docker 镜像 tar 文件、`bin/` 下的管理脚本、`conf/install.env.example` 配置模板、`conf/nginx/default.conf` Nginx 配置模板

#### Scenario: 在线安装包内容完整
- **THEN** 包内 SHALL 包含 `bin/` 下的管理脚本、`conf/install.env.example`、`conf/nginx/default.conf`、`conf/docker-compose.yml.template`，镜像从远程 registry 拉取

### Requirement: 生产部署包 SHALL 支持离线安装
部署包 SHALL 通过 `docker save` 导出的 tar 文件分发镜像，安装时通过 `docker load` 加载，无需生产服务器访问外网。

#### Scenario: 从离线 tar 文件加载镜像
- **WHEN** `conf/install.env` 中 `DE_IMAGE_DIR` 指向包含镜像 tar 文件的目录
- **THEN** `install.sh` SHALL 使用 `docker load` 从该目录加载所有镜像
- **AND** SHALL NOT 执行 `docker pull`

#### Scenario: 在线拉取镜像
- **WHEN** `DE_IMAGE_DIR` 为空
- **THEN** `install.sh` SHALL 使用 `docker pull` 从 registry 拉取镜像

### Requirement: 安装目录 SHALL 可配置且统一管理
所有持久化数据（数据库、日志、静态资源、备份）SHALL 通过 bind mount 存放在 `DE_INSTALL_DIR` 指定的目录下，默认为 `/opt/module/pydataease`。

#### Scenario: 自定义安装目录
- **WHEN** `DE_INSTALL_DIR=/opt/custom/path` 配置在 `install.env` 中
- **THEN** `install.sh` SHALL 在 `/opt/custom/path` 下创建 `data/`、`logs/`、`static/`、`conf/`、`release/` 子目录
- **AND** `docker-compose.yml` 的 volumes SHALL 绑定挂载到这些子目录

#### Scenario: 默认安装目录
- **WHEN** `DE_INSTALL_DIR` 未配置
- **THEN** SHALL 使用 `/opt/module/pydataease` 作为默认值

### Requirement: 已安装版本 SHALL 可查询
安装完成后 SHALL 在安装目录下记录版本信息，供升级和回滚时读取。

#### Scenario: 版本文件写入
- **WHEN** `install.sh` 成功完成安装
- **THEN** `release/VERSION` 文件 SHALL 包含已安装的版本号

#### Scenario: 升级时版本比较
- **WHEN** `upgrade.sh` 读取 `release/VERSION` 获取当前版本
- **THEN** SHALL 将当前版本与新版本比较，如果版本相同 SHALL 提示用户并退出
