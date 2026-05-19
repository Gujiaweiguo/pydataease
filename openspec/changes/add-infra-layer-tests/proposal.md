## Why

前端基础设施层（Router、Directives、Plugins）是应用的骨架——路由守卫控制页面访问权限，指令封装了权限校验和交互行为，插件负责 UI 库和国际化初始化。这些模块被全量页面依赖，但当前完全无测试覆盖。添加测试可以防止导航逻辑、权限控制和插件初始化被意外破坏。

## What Changes

为以下三个基础设施模块添加测试文件：

- **Router** (`src/router/`): 测试路由配置、导航守卫（鉴权/重定向）、路由元信息
- **Directives** (`src/directive/`): 测试 Permission 指令（权限校验）、ClickOutside 指令（点击外部关闭）
- **Plugins** (`src/plugins/`): 测试 element-plus 插件安装、vue-i18n 国际化插件初始化

所有变更只涉及新增测试文件，不修改任何生产代码。

## Capabilities

### New Capabilities
- `router-tests`: 路由配置与导航守卫测试，包含鉴权跳转、路由元信息、404 兜底
- `directive-tests`: 权限指令和点击外部指令测试，包含 v-permission、v-click-outside
- `plugin-tests`: 前端插件初始化测试，包含 element-plus、vue-i18n 的 setup 流程

### Modified Capabilities
（无——本 change 不修改现有 spec 行为）

## Impact

- 新增测试文件，无生产代码变更
- 影响范围：仅 `core/core-frontend/` 目录
- 验证门禁：L0 frontend（ts:check, lint） + 测试通过
- 无需 Docker、打包或运行环境验证
