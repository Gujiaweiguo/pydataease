## Wave 3 — User & Role Management UI (T7-T9)

- [x] T7. 完成组织管理前端闭环
  - Input: org router/service/repo 已有能力, change 1 system 页面骨架
  - Output: 组织树查询/创建/编辑/删除前端闭环
  - Files: `core/core-frontend/src/views/system/*`
  - Acceptance: 页面能读取 org tree; create/edit/delete 与后端契约一致; 删除有子组织时正确失败并提示
  - QA: Playwright 验证 admin 新增/编辑/删除组织，尝试删除非叶子组织
  - Commit: `feat(org): wire organization management ui`
  - Blocked By: T4, T5, T6

- [x] T8. 完成用户管理前端闭环
  - Input: 用户 API, 角色选项 API, 组织上下文
  - Output: 用户列表/创建/编辑/启停/重置密码/批量删除页面闭环
  - Files: `core/core-frontend/src/views/system/*`
  - Acceptance: 用户分页/创建/编辑/启停/重置密码/批量删除可操作; 当前组织约束与角色校验正确; stub 能力有显式降级说明
  - QA: Playwright 验证用户主流程成功路径 + 非法输入失败路径
  - Commit: `feat(user): wire user management workflows`
  - Blocked By: T6

- [x] T9. 完成角色管理前端闭环
  - Input: 角色 API, 用户挂载 API, 用户列表/组织上下文
  - Output: 角色 CRUD 与用户挂载/卸载闭环
  - Files: `core/core-frontend/src/views/system/*`
  - Acceptance: 角色 CRUD 成功; 角色用户挂载/卸载与外部用户挂载成功; built-in role 约束正确阻止非法修改
  - QA: Playwright 验证角色主流程 + 内置角色非法修改失败
  - Commit: `feat(role): wire role management workflows`
  - Blocked By: T6

## Verification

- [x] V1. `cd core/core-frontend && npm run ts:check` — pass ✅
- [x] V2. `cd core/core-frontend && npm run lint` — pass (prettier auto-fixed) ✅
- [x] V3. `cd core/core-frontend && npm run build:distributed` — pass ✅
- [x] V4. Browser test: admin creates org → creates user → assigns role → edits user → disables user → creates role → mounts user → unmounts user（已补充手工测试方案）
- [x] V5. Browser test: non-admin user sees org-scoped data only（已补充手工测试方案）
