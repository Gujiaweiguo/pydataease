## Why

官方手册（https://dataease.cn/docs/v2/xpack/sys_management_permission/#3）定义的权限管理语义与当前实现之间存在 7 类可验证缺口：资源权限可配置但未全面强制执行、行权限缺少系统变量维度、组织隔离范围超出文档承诺、数据源仅查看约束未闭环、列权限自定义掩码未落地、前端权限消费粒度过粗、菜单授权模型口径不一致。这些缺口会导致越权风险、数据暴露或产品承诺不可信。

## What Changes

- **P0-1 资源权限后端强制校验闭环**：将 dashboard/screen/dataset/datasource 的读、改、导出、授权接口统一接入 `require_resource` 或 service 层统一校验；废弃 `checkPermission` 桩实现改为真实校验。
- **P0-2 补齐 sysvar 行权限执行链路**：在 `DataPermissionService.collect_row_filters()` 中增加系统变量解析，将用户系统变量值映射为行权限过滤条件。
- **P0-3 组织隔离范围校正**：区分组织树展示范围与资源访问范围，收窄非 admin 用户可见的组织树为仅当前组织（不含祖先/后代），与手册"严格隔离"语义对齐。
- **P0-4 数据源 view-only 约束补强**：在数据源/数据集编辑/创建后端接口补 view/manage 分离校验，确保仅查看权限用户无法通过 API 创建或修改数据集。
- **P1-1 列权限自定义掩码规则**：在列权限模型中增加 mask_start/mask_end 参数，后端按规则执行区间掩码，前端 RowColumnPermission.vue 增加配置 UI。
- **P1-2 前端权限粒度细化**：`v-permission` 指令改为支持 capability 表达（如 `['dataset:export']`），前端从统一的 capability 状态消费权限。
- **P2-1 菜单权限模型口径收敛**：明确保留 role-only 菜单授权，移除 user/org 维度菜单授权的执行逻辑（保留模型以兼容数据），更新文档口径。

## Capabilities

### New Capabilities
- `resource-permission-enforcement`: 资源权限后端强制校验闭环，覆盖 dashboard/screen/dataset/datasource 四类资源的 view/manage/authorize/export 操作
- `sysvar-row-permission`: 行权限系统变量解析与执行，支持按系统变量值过滤数据行
- `datasource-view-only-guard`: 数据源仅查看权限约束，阻止 view-only 用户创建/编辑数据集

### Modified Capabilities
- `organization-model`: 收窄非 admin 组织树可见范围为仅当前组织，对齐手册严格隔离语义
- `row-column-security`: 列权限增加自定义区间掩码规则（mask_start/mask_end）
- `permission-config-ui`: 前端权限消费模型从 anyManage 改为 capability 表达
- `menu-authorization`: 收敛菜单授权为 role-only，移除 user/org 维度执行逻辑

## Impact

- **后端服务层**：`permission_service.py`, `data_permission_service.py`, `auth_permission_service.py`, `org_service.py`, `menu_service.py`, `column_permission_service.py`, `row_permission_service.py`, 各业务 router
- **前端页面**：`permission/index.vue`, `RowColumnPermission.vue`, `directive/Permission/index.ts`, `store/modules/interactive.ts`, `store/modules/permission.ts`
- **数据库**：`core_column_permission` 表需增加 mask_start/mask_end 字段（需 migration）
- **测试**：需补充资源权限强制校验、sysvar 行权限、组织隔离、数据源 view-only、列权限掩码等自动化测试
- **Gate 层级**：涉及 API/auth/repository + database changes → L0 backend + L1 backend + L2 backend（migration）
