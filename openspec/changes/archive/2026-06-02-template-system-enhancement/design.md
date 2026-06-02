## Context

模板系统有两个独立子系统：

1. **模板管理**（`/templateManage/*`）— 完整可用，20 个端点，管理本地 `visualization_template` 表中的模板 CRUD + 分类。
2. **模板市场**（`/templateMarket/*`）— 空壳。`TemplateMarketService` 所有方法返回空数组，仅从 `sys_setting` 读取 `template.url`（无默认值）。

前端模板市场页面（`views/template-market/index.vue`）从 `GET /templateMarket/search` 获取数据，期望的数据结构：
- `contents`: 数组，每项含 `title`, `thumbnail`, `id`, `templateType`（"PANEL"/"SCREEN"）, `source`（"market"/"manage"）, `classify`, `categoryNames`, `metas.theme_repo`
- `categories`: 数组，每项含 `label`, `value`, `source`
- `baseUrl`: 字符串（用于拼接缩略图 URL）

关键发现：当 `source=manage` 时，前端应用模板走 `templateId`（本地模板 ID），即已有的模板管理路径。这意味着只要后端返回 `source=manage` 的 content items，整个模板市场就能用本地模板正常工作。

已有的仪表板/大屏导出功能（`imgUtils.ts` 的 `download2AppTemplate()`）将 canvas 快照 + 样式 + 数据打包为 `.DET2` JSON 文件。导入功能（`DeTemplateImport.vue`）解析 `.DET2` 文件并存入 `visualization_template` 表。两者数据格式一致。

## Goals / Non-Goals

**Goals:**
- 模板中心市场从本地 `visualization_template` 表读取数据，首页推荐区和全页模板中心都有内容
- 本地模板管理页面支持将已保存的模板导出为 `.DET2` 文件
- 预置 seed 数据（仪表板 + 大屏模板），确保开箱即有内容展示

**Non-Goals:**
- 不实现外部 marketplace 接入（不依赖 `template.url`）
- 不修改 `.DET2` 文件格式
- 不修改仪表板/大屏编辑器中已有的"导出为模板"功能
- 不新增数据库表或 migration（复用现有 `visualization_template` + `visualization_template_category` + `visualization_template_category_map`）

## Decisions

### 1. TemplateMarketService 重写：查询本地数据库

**选择**：将 `TemplateMarketService` 从返回空 stub 改为查询 `visualization_template` 表，将模板记录映射为前端期望的 content item 格式。

**理由**：
- 前端已有 `source=manage` 路径，应用模板时直接使用 `templateId`，无需任何外部 URL
- 数据已在本地，无需网络请求
- 前端无需修改数据获取逻辑，只需后端返回格式正确即可

**字段映射**：
```
visualization_template → market content item
  id            → id
  name          → title
  snapshot      → thumbnail (base64 data URL，已有 `static-resource` 前缀走 imgUrlTrans)
  dv_type       → templateType ("PANEL"/"SCREEN")
  node_type     → templateType 补充 ("template"/"app")
  template_type → source 统一为 "manage"
  (固定值)       → classify: "推荐"
  (固定值)       → categoryNames: 从 category_map + category 表联查
  (固定值)       → metas: { theme_repo: "" } (manage 模式不需要)
```

**替代方案**：保持后端 stub，前端直接调 `/templateManage/*` API。放弃——需要大改前端数据流，风险更高。

### 2. 缩略图处理

**选择**：seed 模板使用 base64 data URL 作为 snapshot（与现有导入逻辑一致），前端 `imgUrlTrans()` 已能处理包含 `static-resource` 的 URL。对于 base64 snapshot，前端直接显示即可。

**理由**：模板的 snapshot 字段已经存储 base64 图片数据，无需额外的图片服务。

### 3. 分类策略

**选择**：复用 `visualization_template_category` 表的现有分类结构。seed 脚本创建 "仪表板模板" 和 "大屏模板" 两个顶级分类。`get_categories()` 返回这些分类，`get_categories_object()` 在原有 "最近/推荐" 基础上追加数据库分类。

### 4. 导出端点

**选择**：新增 `GET /templateManage/export/{template_id}`，返回模板的完整 JSON（`templateStyle` + `templateData` + `dynamicData` + `snapshot` + 元信息），格式与 `.DET2` 文件一致。前端用 `FileSaver` 下载。

**理由**：与现有导入格式完全兼容，导出的文件可以直接在另一个实例上导入。

**替代方案**：前端直接从已有的 `findOne` 端点获取数据并拼装 JSON。放弃——字段名映射不一致（DB 用 `template_style` vs .DET2 用 `canvasStyleData`），在服务端做映射更可靠。

### 5. Seed 脚本

**选择**：创建 `scripts/seed_template_data.py`，幂等插入模板数据。模板内容使用简化版（空白仪表板/大屏框架 + 基础组件），不依赖外部数据源。

**理由**：与已有的 `seed_demo_data.py` 风格一致。幂等设计避免重复执行产生重复数据。

## Risks / Trade-offs

- **[模板内容质量]** → seed 模板是简化的框架模板，不是复杂的成品看板。后续可通过管理界面导入更多 .DET2 模板丰富内容。
- **[性能]** → `search_recommend` 查询所有模板，数据量大时可能有性能问题。Mitigation：限制返回数量（最多 8 条），按创建时间倒序。
- **[分类映射]** → 前端 categories 的 `source` 字段决定筛选行为。如果 DB 分类没有 `source` 字段可能导致筛选异常。Mitigation：所有本地分类统一标记 `source=manage`。
- **[缩略图大小]** → base64 snapshot 存在数据库中会增加查询负载。Mitigation：snapshot 已是 JPEG 质量 0.1 压缩的，实际大小可控。
