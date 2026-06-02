## Why

目前左上角导航栏 Logo 和"关于"弹窗的背景图、产品描述等内容均硬编码在前端静态资源中。管理员无法通过后台自定义这些品牌元素，导致每个实例看起来都一样，无法体现企业个性化品牌。让这些元素可后台配置是产品白标化（white-labeling）的基础需求。

## What Changes

- 在系统参数的**外观 tab** 中增加 Logo 图片上传配置项，用于替换导航栏左上角 logo（及登录页 logo）
- 在系统参数中**新增独立的"关于"tab**，用于配置"关于"弹窗的可定制内容：
  - 关于页背景图（替换硬编码的 `about-bg.png`）
  - 关于页产品描述文案（自定义 HTML/纯文本）
  - 关于页 logo（可复用导航栏 logo 或单独配置）
- 后端在已有的 `sys_setting` key-value 体系中新增对应 key（如 `ui.logo`、`ui.aboutBg`、`ui.aboutContent`、`ui.aboutLogo`），不新增数据表或 migration
- 前端 `appearanceStore` 扩展，读取新增的 key
- 前端 `about/index.vue` 从 appearance store 读取可配置内容，保留已有的 license 信息展示逻辑

## Capabilities

### New Capabilities

- `branding-config-ui`: 系统参数中新增品牌配置能力——外观 tab 的 logo 上传、新增"关于"tab 的背景图/描述/logo 编辑。涵盖后端 setting key 定义、前端配置表单、appearance store 扩展、about 组件改造。

### Modified Capabilities

（无已有 spec 的需求变更）

## Impact

**后端（`core/pydataease-backend/`）**:
- `app/settings/defaults.py` — 新增 `ui.logo`、`ui.aboutBg`、`ui.aboutContent`、`ui.aboutLogo` 等 key
- `app/routers/bootstrap.py` — `GET /sysParameter/ui` 返回值自动包含新 key（已有机制，无需改动）
- `app/routers/system.py` — `POST /sysParameter/appearance/save` 已支持任意 `ui.*` key（已有机制，无需改动）
- 可能需要检查图片上传是否复用现有 `StaticResourceService` 或需要新的图片服务端点

**前端（`core/core-frontend/`）**:
- `src/store/modules/appearance.ts` — 扩展 state 和 getter 支持新 key
- `src/views/system/parameter/appearance/index.vue` — 增加 logo 上传控件
- `src/views/system/parameter/index.vue` — 新增"关于"tab 注册
- `src/views/system/parameter/about/index.vue` — 新建：关于配置表单组件
- `src/views/about/index.vue` — 改为从 appearance store 读取背景图、描述、logo
- `src/layout/components/Header.vue` / `HeaderSystem.vue` — logo 读取逻辑已有，确认与新 key 对接

**测试**:
- 后端 `tests/test_appearance_settings.py` — 扩展覆盖新 key
- Gate: L0 (ruff + ts:check) + L1 (pytest)
