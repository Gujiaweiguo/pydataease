## Why

模板中心市场（Template Market）的后端 `TemplateMarketService` 是一个空壳——所有方法返回空数组，`template.url` 配置无默认值，导致首页"模板中心"区域始终为空。同时，本地模板管理页面缺少"导出"功能——用户创建的仪表板/大屏可以通过预览页导出为 `.DET2` 模板文件，但已保存到模板管理中的模板无法再次导出分享。这两个缺口使得整个模板系统无法形成"创建→导出→导入→复用"的完整闭环。

## What Changes

- **模板中心市场改用本地数据源**：重写 `TemplateMarketService`，将 `/templateMarket/*` 端点的数据来源从外部 marketplace URL 改为本地 `visualization_template` 表。前端无需切换数据源，只需适配返回格式。
- **内置模板 seed 数据**：提供 seed 脚本，向 `visualization_template` + `visualization_template_category` 表预置一批仪表板和大屏模板（复用已有的 demo 数据），确保模板中心开箱即有内容。
- **本地模板管理增加"导出"按钮**：在模板管理页面（`/template`）为已保存的模板添加导出功能，将 `templateStyle` + `templateData` + `dynamicData` + `snapshot` 等字段打包为 `.DET2` JSON 文件下载。数据格式与现有 `imgUtils.ts` 的 `download2AppTemplate()` 输出一致。
- **后端新增模板导出端点**：`GET /templateManage/export/{id}` 返回指定模板的完整 JSON，供前端下载。

## Capabilities

### New Capabilities

- `template-local-market`：模板中心从本地数据库读取模板数据，替代外部 marketplace。包括 `TemplateMarketService` 重写、seed 脚本、前端数据适配。
- `template-export`：本地模板管理的导出功能，将已保存模板导出为 `.DET2` 文件。

### Modified Capabilities

（无——现有 specs 不涉及模板系统）

## Impact

- **后端**：`services/template_market_service.py` 重写（从 stub 改为读取 `visualization_template` 表）；`routers/template.py` 新增导出端点；`settings/defaults.py` 无需新增 key。
- **前端**：模板管理页（`views/template/`）增加导出按钮和下载逻辑；模板中心（`views/template-market/`）可能需要适配本地数据的字段映射差异。
- **数据库**：需要 seed 脚本预置模板和分类数据。无需 migration（表结构不变）。
- **测试**：后端需覆盖 `TemplateMarketService` 新逻辑 + 导出端点；前端 ts:check + lint。

**Gate layer**: L0（ruff + ts:check + lint）+ L1（pytest）。无 API contract breaking change，无需 L2+。
