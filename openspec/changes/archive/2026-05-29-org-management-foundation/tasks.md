## Wave 1 — Baseline & Root Cause (T1-T3)

- [x] T1. 固化官方能力基线
  - Input: 官方手册 URLs, 现有调研结论
  - Output: 结构化能力矩阵（组织/用户/角色/权限/行列权限/依赖/异常）
  - Acceptance: 能力矩阵覆盖五大块；区分"官方事实/默认解释/待验证边界"
  - QA: 检查能力矩阵产物覆盖 org/user/role/menu-resource/row-column

- [x] T2. 固化仓库差异与当前根因
  - Input: 仓库代码、数据库种子、动态路由链路
  - Output: 差异分析与根因列表（菜单元数据缺失/页面组件缺失/权限点缺失/标题路由映射缺失）
  - Acceptance: 根因列表能解释 admin 为何看不到后台入口；后端能力标记为"存在但入口未闭环"
  - QA: 每个根因有文件或数据证据

- [x] T3. 确认 change 拆分与阶段顺序
  - Input: T1 能力基线, T2 差异, Oracle/Metis 建议
  - Output: 4-change 最终拆分定义
  - Acceptance: 明确保持 4 个 change 的理由；明确 change 1 为何必须纳入 admin visibility
  - QA: 每个 change 的输出恰好是后一个 change 的输入

## Wave 2 — Admin Visibility Foundation (T4-T6)

- [x] T4. 设计后台入口菜单与权限点扩展
  - Input: 当前 `core_menu`, `core_permission_point` 种子
  - Output: 菜单/权限点扩展设计与迁移
  - Files: `core/pydataease-backend/alembic/versions/*`
  - Acceptance: 新增菜单树可被 `/menu/query` 使用；权限点覆盖后台管理菜单粒度；迁移幂等可回滚
  - QA: 迁移后查询 core_menu 检查 system/org/user/role/permission 节点
  - Commit: `feat(auth): seed admin console menu foundation`

- [x] T5. 对齐菜单标题映射与动态路由契约
  - Input: 新后台入口树命名, 前端 component path 设计
  - Output: title/path/component 映射方案
  - Files: `core/pydataease-backend/app/services/menu_service.py`, `core/core-frontend/*`
  - Acceptance: 每个新增入口有有效 title 与 component path；前端 ts/build 通过
  - QA: 运行前端 ts:check + build，确认无 missing module
  - Commit: `feat(menu): align admin route metadata`

- [x] T6. 交付 change 1 最小系统页面骨架
  - Input: admin console 菜单结构, 前端 system 目录规范, 现有 API clients
  - Output: 可渲染的 org/user/role/permission 页面骨架
  - Files: `core/core-frontend/src/views/system/*`
  - Acceptance: admin 能通过动态菜单访问各页面；页面不报错/不白屏；非授权路径按路由守卫处理
  - QA: Playwright 验证 admin 登录后点击各菜单均能进入非空页面
  - Commit: `feat(system): add admin console shell pages`
  - Blocked By: T4, T5

## Verification

- [x] V1. `cd core/pydataease-backend && uv run ruff check .` — zero errors
- [x] V2. `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass (36 passed, 22 skipped)
- [x] V3. `cd core/pydataease-backend && uv run alembic upgrade head` — migration succeeds
- [x] V4. `cd core/core-frontend && npm run ts:check && npm run build:distributed` — pass
- [x] V5. Browser test: admin login → see admin console menu → click org/user/role/permission → non-blank pages — ALL PASS
