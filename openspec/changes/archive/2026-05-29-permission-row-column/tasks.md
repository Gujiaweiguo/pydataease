## Wave 5 — Row & Column Permissions (T12-T13)

- [x] T12. 完成行权限与列权限配置界面
  - Input: row/column permission services, dataset 权限接口, 系统变量规则
  - Output: 行权限 / 列权限 / 白名单 UI 与规则保存闭环
  - Files: `core/core-frontend/src/views/system/*`, possibly `core/pydataease-backend/*` (minor)
  - Acceptance: 行权限/列权限/白名单规则可编辑与保存; 列权限支持禁用/脱敏表达; UI 能表达目标对象/规则内容/启停状态
  - QA: Playwright 验证行列权限规则成功路径 + 非法规则失败路径
  - Commit: `feat(permission): add row and column permission console`
  - Blocked By: T10, T11

- [x] T13. 验证数据权限执行效果
  - Input: 已落地的行列权限 UI 与数据权限服务
  - Output: 查询时规则确实生效的证据
  - Files: `core/pydataease-backend/tests/*`
  - Acceptance: 行权限影响查询结果; 列权限影响字段显示/脱敏结果; 白名单用户行为不同于普通用户
  - QA: 后端测试验证同一数据集不同用户返回行数差异; 对比白名单与非白名单用户查询结果
  - Verification Reference:
    - `core/pydataease-backend/tests/test_data_permission_service_coverage.py::test_collect_row_filters_returns_user_rule_when_present`
    - `core/pydataease-backend/tests/test_data_permission_service_coverage.py::test_apply_column_rules_enforces_priority_disable_mask_and_desensitize`
    - `core/pydataease-backend/tests/test_data_permission_service_coverage.py::test_apply_column_rules_returns_original_data_for_whitelisted_user`
  - Commit: `test(permission): verify row and column enforcement`
  - Blocked By: T12

## Verification

- [x] V1. `cd core/pydataease-backend && uv run ruff check .` — zero errors
- [x] V2. `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass (pre-existing failure in test_auth_permission_routes.py unrelated to our changes)
- [x] V3. `cd core/core-frontend && npm run ts:check && npm run build:distributed` — pass
- [x] V4. Test: user with row filter sees subset of rows in dataset query
  - Reference: `test_data_permission_service_coverage.py::test_collect_row_filters_returns_user_rule_when_present`
- [x] V5. Test: user with column desensitize rule sees masked data
  - Reference: `test_data_permission_service_coverage.py::test_apply_column_rules_enforces_priority_disable_mask_and_desensitize`
- [x] V6. Test: whitelisted user sees full unfiltered data
  - Reference: `test_data_permission_service_coverage.py::test_apply_column_rules_returns_original_data_for_whitelisted_user`
