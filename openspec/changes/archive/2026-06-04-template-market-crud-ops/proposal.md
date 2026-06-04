## Why

模板市场页（`/template-market`）目前是纯浏览 + 应用模板的界面。用户如果想上传、下载或删除模板，必须跳转到独立的模板管理页（`/template-manage`）。这导致用户在浏览模板时发现需要管理操作时，需要中断当前流程切换页面，体验割裂。将 CRUD 操作直接带到模板市场页，让用户在同一个上下文中完成浏览、应用和管理。

## What Changes

- 在模板市场页的模板卡片上增加**下载（导出）**和**删除**操作入口
- 在模板市场页的工具栏增加**上传（导入）**按钮，复用现有 `.DET2/.DET2APP` 文件导入流程
- 复用现有后端 API（`/templateManage/export/{id}`、`/templateManage/save`、`/templateManage/delete/{id}/{categoryId}`），不新增后端端点
- 操作按钮遵循现有权限体系：只有有权限的用户才能看到和执行删除操作
- 操作完成后刷新当前模板市场列表，保持浏览上下文不丢失

## Capabilities

### New Capabilities
- `template-market-crud-actions`: 模板市场页面的上传/下载/删除操作能力 — 在模板市场浏览界面直接执行导入、导出和删除，无需跳转到模板管理页

### Modified Capabilities
<!-- 无需修改现有 spec — 后端 API 不变，只改前端 UI 交互层 -->

## Impact

- **前端**：`views/template-market/index.vue` 及其子组件（`TemplateMarketV2Item.vue`、`MarketPreviewV2.vue`）需要增加操作按钮和交互逻辑
- **后端**：无新增端点，复用 `/templateManage/` 现有 CRUD API
- **Gate 层级**：L0 前端（`ts:check` + `lint` + `lint:stylelint`），涉及 UI 变更但无路由/打包结构变化，无需前端 build gate
