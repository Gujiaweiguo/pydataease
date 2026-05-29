## Wave 4 — Permission Configuration UI (T10-T11)

- [x] T10. 完成菜单权限与资源权限配置界面
  - Input: auth API, menu/resource trees, 用户角色组织上下文
  - Output: 菜单权限 / 资源权限 / 目标权限配置闭环
  - Files: `core/core-frontend/src/views/system/*`, possibly `core/pydataease-backend/*` (minor)
  - Acceptance: 菜单树与资源树可加载; 保存授权后后端状态更新; admin 与非 admin 授权可见性差异可验证
  - QA: Playwright 验证菜单授权成功路径 + 资源授权越权失败路径
  - Commit: `feat(auth): add menu and resource permission console`
  - Blocked By: T7, T8, T9

- [x] T11. 校准授权边界与 `/menu/query` 生效联动
  - Input: 菜单授权 UI, 后端 permission service, 组织/角色层规则
  - Output: 授权边界与动态菜单生效规则稳定化
  - Files: `core/pydataease-backend/*`, `core/core-frontend/*`
  - Acceptance: 授权保存后 `/menu/query` 生效行为有稳定规则; 不出现 org 泄漏; 权限不足用户无法修改授权配置
  - QA: Playwright 验证授权后菜单联动 + 跨组织越权失败
  - Commit: `fix(auth): align permission enforcement and menu visibility`
  - Blocked By: T10

## Verification

- [x] V1. `cd core/pydataease-backend && uv run ruff check .` — zero errors
- [x] V2. `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass
- [x] V3. `cd core/core-frontend && npm run ts:check && npm run build:distributed` — pass
- [x] V4. Browser test: grant menu permission to role → login as role member → menu changes visible
- [x] V5. Browser test: non-admin cannot access permission configuration
- [x] V6. Browser test: cross-org permission isolation — org A admin cannot modify org B permissions
