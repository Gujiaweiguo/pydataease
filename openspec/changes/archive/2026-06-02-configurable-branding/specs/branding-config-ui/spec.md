## ADDED Requirements

### Requirement: Logo upload in appearance settings
系统参数"外观"tab 中 SHALL 提供 Logo 图片上传控件。管理员可上传自定义 Logo 图片，用于替换导航栏左上角和登录页的默认 Logo。

上传的图片 SHALL 通过已有的 `StaticResourceService`（或 `/appearance/image/` 端点）存储，并在 `sys_setting` 中以 `ui.navigate`（导航栏 Logo）和 `ui.login`（登录页 Logo）key 记录图片标识。

外观 tab 的 Logo 上传控件 SHALL 支持预览当前已上传的 Logo，并支持删除恢复为默认 Logo。

#### Scenario: Admin uploads navigation bar logo
- **WHEN** 管理员在外观 tab 上传一张 Logo 图片并保存
- **THEN** 系统将图片存储并记录 `ui.navigate` key，前端 appearance store 加载后 `getNavigate` getter 返回新 Logo URL，Header.vue 和 HeaderSystem.vue 显示上传的 Logo 替代默认 `logo.svg`

#### Scenario: Admin uploads login page logo
- **WHEN** 管理员在外观 tab 上传登录页 Logo 图片并保存
- **THEN** 系统将图片存储并记录 `ui.login` key，前端 appearance store 加载后 `getLogin` getter 返回新 Logo URL，登录页显示上传的 Logo 替代默认 `DataEase.svg`

#### Scenario: Admin clears custom logo
- **WHEN** 管理员在外观 tab 删除已上传的 Logo 并保存
- **THEN** `ui.navigate`（或 `ui.login`）值被清空，前端回退到默认静态 Logo（`logo.svg` 或 `DataEase.svg`）

#### Scenario: Non-admin user views navigation
- **WHEN** 普通用户（非管理员）访问系统
- **THEN** 导航栏和登录页 SHALL 显示管理员配置的 Logo；如果未配置则显示默认 Logo

### Requirement: About configuration tab
系统参数页 SHALL 新增独立的"关于"tab，管理员可在其中配置"关于"弹窗的可定制内容：背景图、产品描述文案、Logo。

"关于"tab 的配置数据 SHALL 使用 `sys_setting` key-value 体系存储，key 前缀为 `ui.`。

#### Scenario: Admin navigates to about tab
- **WHEN** 管理员打开系统参数设置页
- **THEN** 在 tab 列表中可见"关于"tab（label 由 i18n key 提供），位于现有 tab 之间，无 feature flag 门控

#### Scenario: About tab shows current configuration
- **WHEN** 管理员切换到"关于"tab
- **THEN** 页面 SHALL 加载并显示当前关于弹窗的背景图、产品描述文案、Logo 的配置状态（已上传图片的预览、已填写的文案内容）

### Requirement: About background image configuration
"关于"tab 中 SHALL 提供背景图上传控件。管理员可上传自定义背景图替换"关于"弹窗中硬编码的 `about-bg.png`。

上传的背景图 SHALL 通过已有的图片存储机制保存，并在 `sys_setting` 中以 `ui.aboutBg` key 记录。

#### Scenario: Admin uploads about background image
- **WHEN** 管理员在"关于"tab 上传背景图并保存
- **THEN** 系统将图片存储并记录 `ui.aboutBg` key

#### Scenario: About dialog displays custom background
- **WHEN** 用户打开"关于"弹窗，且管理员已配置自定义背景图
- **THEN** 弹窗顶部 banner 区域 SHALL 显示管理员上传的背景图，替代默认 `about-bg.png`；未配置时 SHALL 保持显示默认 `about-bg.png`

### Requirement: About product description configuration
"关于"tab 中 SHALL 提供产品描述文案的文本编辑区域。管理员可输入自定义的产品介绍、联系方式等内容。

文案内容 SHALL 以 `ui.aboutContent` key 存储在 `sys_setting` 中。

#### Scenario: Admin saves about description text
- **WHEN** 管理员在"关于"tab 填写产品描述文案并保存
- **THEN** 系统将文案存储到 `ui.aboutContent` key

#### Scenario: About dialog displays custom description
- **WHEN** 用户打开"关于"弹窗，且管理员已配置产品描述文案
- **THEN** 弹窗中 license 信息区域之后 SHALL 显示管理员配置的文案内容；未配置时 SHALL 不显示额外的描述区域

### Requirement: About logo configuration
"关于"tab 中 SHALL 提供 Logo 图片上传控件。管理员可上传自定义 Logo 用于"关于"弹窗。

上传的 Logo SHALL 以 `ui.aboutLogo` key 存储在 `sys_setting` 中。如未单独配置，"关于"弹窗 SHALL 回退使用导航栏 Logo（`ui.navigate`），若导航栏 Logo 也未配置则使用默认 `logo.svg`。

#### Scenario: Admin uploads dedicated about logo
- **WHEN** 管理员在"关于"tab 上传专用 Logo 并保存
- **THEN** 系统将图片存储并记录 `ui.aboutLogo` key

#### Scenario: About dialog displays logo with fallback chain
- **WHEN** 用户打开"关于"弹窗
- **THEN** 弹窗 Logo 区域 SHALL 按以下优先级显示：`ui.aboutLogo` > `ui.navigate` > 默认 `logo.svg`

### Requirement: Backend setting keys for branding
后端 SHALL 在 `SETTINGS_DEFAULTS`（`app/settings/defaults.py`）中新增以下 key，默认值为空字符串：

- `ui.navigate`：导航栏 Logo 图片标识
- `ui.login`：登录页 Logo 图片标识
- `ui.aboutBg`：关于弹窗背景图标识
- `ui.aboutContent`：关于弹窗产品描述文案
- `ui.aboutLogo`：关于弹窗专用 Logo 标识

新增的 key SHALL 通过已有的 `GET /sysParameter/ui` 和 `GET /sysParameter/appearance` 端点自动返回，无需新增 API 端点或数据表。

#### Scenario: New keys appear in appearance API response
- **WHEN** 前端调用 `GET /sysParameter/ui` 或 `GET /sysParameter/appearance`
- **THEN** 响应中 SHALL 包含 `ui.navigate`、`ui.login`、`ui.aboutBg`、`ui.aboutContent`、`ui.aboutLogo` key（未配置时值为空字符串）

#### Scenario: New keys are saved via appearance save endpoint
- **WHEN** 前端调用 `POST /sysParameter/appearance/save` 并包含新的 `ui.*` key
- **THEN** 系统 SHALL 正确持久化这些值到 `core_sys_setting` 表

### Requirement: Appearance store extension
前端 `appearanceStore`（`src/store/modules/appearance.ts`）SHALL 扩展 state 以支持新增的 key：`aboutBg`、`aboutContent`、`aboutLogo`。

Store SHALL 提供对应的 getter 方法，对于图片类型的 key（`aboutBg`、`aboutLogo`）返回拼接后的完整 URL（`baseUrl + value`），文案类型的 key（`aboutContent`）返回原始文本。

#### Scenario: Store returns custom about background URL
- **WHEN** `appearanceStore` 已加载且 `ui.aboutBg` 有值
- **THEN** `getAboutBg` getter SHALL 返回 `basePath + '/appearance/image/' + aboutBg` 格式的完整 URL

#### Scenario: Store returns about content text
- **WHEN** `appearanceStore` 已加载且 `ui.aboutContent` 有值
- **THEN** `getAboutContent` getter SHALL 返回文案文本内容
