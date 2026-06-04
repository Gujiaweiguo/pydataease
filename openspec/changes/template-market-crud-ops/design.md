## Context

模板市场页（`/template-market`）是用户浏览和应用模板的主界面，包含三个视图模式：
- **`full`** — 主浏览视图（左侧分类树 + 右侧模板卡片网格），工具栏已有"打开导入入口"按钮跳转到 `/template-manage`
- **`marketPreview`** — 预览视图（左侧模板列表 + 右侧大图预览），通过 `MarketPreviewV2` 组件实现
- **`createPreview`** — 创建预览视图（大图 + 前后翻页 + 应用按钮）

模板卡片组件 `TemplateMarketV2Item` 目前只有"预览"和"应用"两个按钮。

后端已有完整的 CRUD API（`/templateManage/export/{id}`、`/templateManage/save`、`/templateManage/delete/{id}/{categoryId}`），前端 `views/template/` 下也有完整的导入/导出/删除 UI 逻辑可复用。

## Goals / Non-Goals

**Goals:**
- 在模板市场页的模板卡片上增加下载（导出）和删除操作按钮
- 在模板市场页工具栏增加上传（导入）按钮，复用现有 `DeTemplateImport` 组件
- 操作完成后刷新当前列表，保持筛选/分类上下文
- 遵循现有权限体系（`createAuth` prop 控制）

**Non-Goals:**
- 不新增后端 API 端点
- 不修改模板管理页（`/template-manage`）的现有功能
- 不增加批量操作（批量删除/批量导出）
- 不修改模板数据结构或存储方式
- 不增加权限模型变更

## Decisions

### D1: 操作按钮放在卡片 hover 区域

**选择**：在 `TemplateMarketV2Item` 的底部滑出区域（现有"预览"/"应用"按钮旁）增加"下载"和"删除"图标按钮。

**备选方案**：
- (a) 卡片右上角三点菜单下拉 — 更常见的管理模式，但增加点击层级
- (b) 工具栏全局操作 — 不适合单模板操作

**理由**：现有卡片已有 hover 滑出区域，新增按钮复用同一交互模式最自然。下载用图标按钮，删除用带确认的图标按钮，视觉上跟现有"预览"/"应用"并列。

### D2: 上传按钮放在工具栏

**选择**：替换现有的"打开导入入口"按钮为直接的"上传模板"按钮，点击弹出 `DeTemplateImport` 对话框（复用 `views/template/component/DeTemplateImport.vue`）。

**理由**：用户当前需要跳转到另一个页面才能导入，换成弹窗导入减少上下文切换。`DeTemplateImport` 是独立对话框组件，可以直接在模板市场页复用。

### D3: 删除前二次确认

**选择**：删除操作弹出 `ElMessageBox.confirm` 确认对话框。

**理由**：删除是不可逆操作，必须确认。复用 Element Plus 的确认对话框，跟模板管理页的删除流程保持一致。

### D4: 操作后刷新列表

**选择**：导入/删除成功后，调用模板市场页已有的 `initSearch` 方法刷新数据。

**理由**：保持筛选条件和分类选择不变，只刷新模板数据。避免用户重新导航。

### D5: 不在预览模式（marketPreview）加 CRUD

**选择**：CRUD 操作只在 `full` 模式的卡片上暴露，不在 `marketPreview` 和 `createPreview` 模式中添加。

**理由**：预览模式聚焦于查看和应用，混入管理操作会分散注意力。用户如需管理可返回 `full` 模式。

## Risks / Trade-offs

- **[卡片按钮空间]** 增加 2 个按钮可能让卡片底部区域拥挤 → 使用图标按钮而非文字按钮节省空间，下载用 Download 图标，删除用 Delete 图标
- **[DeTemplateImport 依赖]** 复用 `DeTemplateImport` 需要确保该组件不依赖模板管理页的特定状态 → 该组件接收 props 回调，独立可用
- **[删除权限]** 市场页没有现成的删除权限检查 → 暂时对所有有创建权限的用户开放删除，后续可加细粒度权限
