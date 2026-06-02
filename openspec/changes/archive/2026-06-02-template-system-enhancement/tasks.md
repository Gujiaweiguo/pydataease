## 1. 后端：TemplateMarketService 重写

- [x] 1.1 重写 `TemplateMarketService.search()` — 查询 `visualization_template` 表（`node_type=template`），联查 `visualization_template_category_map` + `visualization_template_category` 获取 categoryNames，映射为前端期望的 content item 格式（id, title, thumbnail, templateType, source="manage", classify, categoryNames, metas）
- [x] 1.2 重写 `TemplateMarketService.search_recommend()` — 查询同上，限制返回最多 8 条，按 `create_time` 降序
- [x] 1.3 重写 `TemplateMarketService.search_preview()` — 逻辑与 search 相同，返回相同格式
- [x] 1.4 重写 `TemplateMarketService.get_categories()` — 查询 `visualization_template_category` 中有模板关联的分类，返回分类 label 列表
- [x] 1.5 重写 `TemplateMarketService.get_categories_object()` — 返回固定条目（"最近", "推荐"）+ 数据库分类条目（source="manage"）
- [x] 1.6 为 TemplateMarketService 编写 pytest 测试，覆盖：有模板/无模板/分类映射/recommend 数量限制

## 2. 后端：模板导出端点

- [x] 2.1 在 `routers/template.py` 新增 `GET /templateManage/export/{template_id}` 端点，调用 TemplateService 导出方法
- [x] 2.2 在 `services/template_service.py` 新增 `export_template(template_id)` 方法，查询模板记录并映射为 .DET2 格式（name, dvType, nodeType, snapshot, canvasStyleData←template_style, componentData←template_data, dynamicData←dynamic_data, version=3）
- [x] 2.3 处理 404 情况：模板不存在时返回 404 错误
- [x] 2.4 为导出端点编写 pytest 测试，覆盖：正常导出、模板不存在 404、字段映射正确性

## 3. Seed 数据脚本

- [x] 3.1 创建 `scripts/seed_template_data.py`，幂等地插入 2 个仪表板模板 + 2 个大屏模板到 `visualization_template` 表
- [x] 3.2 创建 "仪表板模板" 和 "大屏模板" 两个分类到 `visualization_template_category` 表，并建立 category_map 映射
- [x] 3.3 模板内容使用简化的仪表板/大屏框架（空白画布 + 基础样式），snapshot 使用占位 base64 图片
- [x] 3.4 执行 seed 脚本并验证数据正确性

## 4. 前端：模板管理导出按钮

- [x] 4.1 在 `views/template/` 模板管理页面的模板操作菜单中添加"导出"按钮
- [x] 4.2 在 `api/template.ts` 新增 `exportTemplate(id)` 函数，调用 `GET /templateManage/export/{id}`
- [x] 4.3 实现下载逻辑：获取 JSON 后使用 FileSaver 保存为 `{name}-TEMPLATE.DET2` 文件
- [x] 4.4 添加 i18n key（中/英/繁）for 导出按钮文案

## 5. 前端：模板中心适配验证

- [x] 5.1 验证首页"模板中心"区域正确显示 seed 模板（缩略图 + 标题）
- [x] 5.2 验证模板中心全页面（`/template-market/index`）能展示模板、分类筛选正常
- [x] 5.3 验证"应用"按钮能正确跳转到仪表板/大屏编辑器并加载模板
- [x] 5.4 处理前端模板卡片缩略图对 base64 snapshot 的显示适配（snapshot 是 data URL 时直接显示，不拼接 baseUrl）

## 6. 验证

- [x] 6.1 后端 ruff check 通过：`cd core/pydataease-backend && uv run ruff check .`
- [x] 6.2 后端 pytest 通过：`cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] 6.3 前端 ts:check 通过：`cd core/core-frontend && npm run ts:check`
- [x] 6.4 前端 lint 通过：`cd core/core-frontend && npm run lint`
- [x] 6.5 浏览器端到端验证：seed 数据 → 模板中心显示 → 应用模板 → 模板管理导出 → 重新导入
