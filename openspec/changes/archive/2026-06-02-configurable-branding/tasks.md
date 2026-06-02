## 1. 后端：Settings Key 定义

- [x] 1.1 在 `core/pydataease-backend/app/settings/defaults.py` 的 `SETTINGS_DEFAULTS` 中新增 key：`ui.navigate`、`ui.login`、`ui.aboutBg`、`ui.aboutContent`、`ui.aboutLogo`，默认值均为空字符串
- [x] 1.2 确认 `/appearance/image/` 图片上传/读取端点是否存在；如不存在，实现图片上传端点（复用现有 `StaticResourceService` 模式或新建）
- [x] 1.3 更新后端测试 `tests/test_appearance_settings.py`，覆盖新增 key 的读取和保存

## 2. 前端：Appearance Store 扩展

- [x] 2.1 在 `src/store/modules/appearance.ts` 的 `AppearanceState` interface 中新增 `aboutBg`、`aboutContent`、`aboutLogo` 字段
- [x] 2.2 在 state 初始化中添加对应默认值（空字符串）
- [x] 2.3 在 getters 中新增 `getAboutBg`（返回 `baseUrl + this.aboutBg`）、`getAboutContent`（返回原始文本）、`getAboutLogo`（返回 `baseUrl + this.aboutLogo`）
- [x] 2.4 在 `setAppearance` action 中将后端返回的 `aboutBg`、`aboutContent`、`aboutLogo` 赋值到 state

## 3. 前端：外观 Tab 增加 Logo 配置

- [x] 3.1 在 `src/views/system/parameter/appearance/index.vue` 的 `APPEARANCE_FORM_KEYS` 中新增 `ui.navigate`、`ui.login`
- [x] 3.2 在外观表单模板中增加导航栏 Logo 和登录页 Logo 的图片上传控件（预览 + 上传 + 删除）
- [x] 3.3 确保图片上传调用现有的图片存储端点，保存时将图片标识写入 `ui.navigate` / `ui.login`

## 4. 前端：新建"关于"Tab

- [x] 4.1 新建 `src/views/system/parameter/about/index.vue`，参照外观 tab 的模式实现表单（load → 编辑 → 保存/重置）
- [x] 4.2 表单包含：背景图上传控件（`ui.aboutBg`）、产品描述文本区域（`ui.aboutContent`）、Logo 上传控件（`ui.aboutLogo`）
- [x] 4.3 定义独立的 `APPEARANCE_ABOUT_KEYS` key 列表（`ui.aboutBg`、`ui.aboutContent`、`ui.aboutLogo`）
- [x] 4.4 添加 i18n key 用于 tab label 和表单 label

## 5. 前端：系统参数页注册"关于"Tab

- [x] 5.1 在 `src/views/system/parameter/index.vue` 的 `allTabs` 数组中新增 `{ label: t('system.about_settings'), name: 'about' }`，无 feature flag
- [x] 5.2 在模板中增加 `<about-settings v-if="activeName === 'about'" />`
- [x] 5.3 导入 `AboutSettings` 组件

## 6. 前端：关于弹窗改造

- [x] 6.1 修改 `src/views/about/index.vue`，背景图从 `appearanceStore.getAboutBg` 读取，无值时回退到默认 `about-bg.png`
- [x] 6.2 Logo 区域实现回退链：`appearanceStore.getAboutLogo` > `appearanceStore.getNavigate` > 默认 `logo.svg`
- [x] 6.3 在 license 信息之后新增产品描述文案区域，从 `appearanceStore.getAboutContent` 读取，无值时不显示

## 7. 验证

- [x] 7.1 后端 L0：`cd core/pydataease-backend && uv run ruff check .`
- [x] 7.2 后端 L1：`cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] 7.3 前端 L0：`cd core/core-frontend && npm run ts:check && npm run lint && npm run lint:stylelint`
- [x] 7.4 手动验证：在外观 tab 上传 Logo → 刷新页面 → 导航栏和登录页显示新 Logo
- [x] 7.5 手动验证：在关于 tab 配置背景图、描述文案、Logo → 打开关于弹窗 → 显示自定义内容
- [x] 7.6 手动验证：清除所有自定义配置 → 关于弹窗和导航栏回退到默认资源
