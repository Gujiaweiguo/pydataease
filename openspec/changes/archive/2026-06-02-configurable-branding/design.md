## Context

当前品牌元素（Logo、关于弹窗内容）硬编码在前端静态资源中。后端已有完整的 `sys_setting` key-value 体系和 appearance API 端点，前端有 `appearanceStore` 和外观配置 tab。本变更在此基础上扩展，不引入新的数据模型或 API 端点。

**当前已存在的图片服务路径**：`/appearance/image/{filename}` — 前端 appearanceStore 已通过 `baseUrl = basePath + '/appearance/image/'` 构造图片 URL。需要确认该端点在后端是否存在且可用。

## Goals / Non-Goals

**Goals:**
- 外观 tab 增加 Logo 上传，可配置导航栏和登录页 Logo
- 系统参数新增"关于"tab，可配置关于弹窗的背景图、描述文案、Logo
- 后端零新端点、零新表、零 migration
- 关于弹窗组件从 appearanceStore 读取配置，保持 license 信息展示逻辑不变

**Non-Goals:**
- 不改动 license 上传/校验逻辑
- 不改动版本号构建号的生成方式
- 不支持富文本编辑器（产品描述为纯文本）
- 不涉及移动端适配（本次仅 PC 端关于弹窗）

## Decisions

### 1. 图片存储：复用现有 `/appearance/image/` 路径

**选择**：使用与当前 `ui.navigate` 相同的图片存储机制。

**理由**：appearanceStore 已经通过 `baseUrl + filename` 构造图片 URL，Header.vue 已有 `<img :src="appearanceStore.getNavigate">` 的完整渲染逻辑。保持一致意味着零前端基础设施改动。

**替代方案**：使用 `StaticResourceService`（base64 存数据库）— 会引入不同的 URL 构造模式，与现有 appearance 图片 URL 体系不一致。

**需要确认**：`/appearance/image/{filename}` 端点的上传和读取是否需要后端改动。如果该端点还不存在，需要新增图片上传端点或在 appearance save 中处理 base64 图片。

### 2. 关于 tab 配置独立于外观 tab

**选择**：新建独立的 `about` tab 组件，使用独立的 `APPEARANCE_ABOUT_KEYS` key 列表和独立表单。

**理由**：配置项的语义不同（视觉风格 vs 产品元信息），受众不同（终端用户感知 vs 管理员维护）。分开更清晰，且与现有 tab 架构一致。

**替代方案**：在外观 tab 内增加折叠区域 — 会导致外观 tab 过长，且语义混乱。

### 3. 关于弹窗 Logo 的回退链

**选择**：`ui.aboutLogo` > `ui.navigate` > 默认 `logo.svg`。

**理由**：大多数用户希望关于弹窗和导航栏用同一个 Logo，单独配置是可选的高级需求。回退链避免了强制用户配置两处。

### 4. 后端 key 定义在 `SETTINGS_DEFAULTS`

**选择**：在 `defaults.py` 的 `SETTINGS_DEFAULTS` dict 中新增 `ui.navigate`、`ui.login`、`ui.aboutBg`、`ui.aboutContent`、`ui.aboutLogo` key，默认值均为空字符串。

**理由**：已有的 `get_ui_settings()` 方法自动合并 `SETTINGS_DEFAULTS` 和数据库值，新增 key 无需改 service/router 代码。`POST /sysParameter/appearance/save` 也已支持任意 `ui.*` key 的持久化。

**注意**：`ui.navigate` 和 `ui.login` 可能已在 Java 原版中存在，但当前 Python 后端的 `SETTINGS_DEFAULTS` 中没有它们。需要确认前端 appearanceStore 的 `setAppearance` 方法中已对这些 key 赋值（第 277-278 行 `this.navigate = data.navigate` 和第 329 行 `this.login = data.login`），说明后端 `/sysParameter/ui` 已可能返回这些字段——只需在 defaults 中声明即可。

### 5. "关于"tab 不加 feature flag 门控

**选择**：tab 定义中不加 `feature` 属性。

**理由**：关于页面配置是基础管理功能，不像外观、嵌入那样可能需要开关控制。与"基础设置"tab 一样始终可见。

## Risks / Trade-offs

- **[图片上传端点可能缺失]** → 需要探索确认 `/appearance/image/` 的后端实现是否存在。如果不存在，需要新增一个图片上传/读取端点，这会增加后端工作量。Mitigation：可先用 `StaticResourceService`（base64）作为临时方案，后续迁移。

- **[defaults.py 新增 key 不影响已有部署]** → 新 key 默认值为空字符串，现有数据库中没有这些 key 时 `get_ui_settings()` 会返回默认空值，前端据此判断显示默认资源。无需 Alembic migration。

- **[外观 tab 表单需扩展 `APPEARANCE_FORM_KEYS`]** → 现有外观 tab 的 `APPEARANCE_FORM_KEYS` 常量需要加入 Logo 相关 key。这是纯前端改动，风险低。

- **[关于弹窗样式可能受自定义背景图尺寸影响]** → 当前 `about-bg.png` 固定 792x180，自定义图片如果尺寸差异大可能导致布局问题。Mitigation：在前端使用 `object-fit: cover` 确保裁切适配。
