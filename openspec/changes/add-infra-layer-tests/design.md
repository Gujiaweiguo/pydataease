## Context

前端 `core/core-frontend/` 有三个基础设施层的测试覆盖缺失：

- **Router** (`src/router/index.ts` + 辅助模块): 定义应用路由、导航守卫、鉴权逻辑。所有页面切换都经过这里。
- **Directives** (`src/directive/`): `Permission` 指令控制元素级权限展示，`ClickOutside` 指令处理点击外部关闭行为。
- **Plugins** (`src/plugins/`): `element-plus` UI 库注册和 `vue-i18n` 国际化初始化。

这些模块的特点是：被全量页面依赖，逻辑相对独立（无深层 Vue 组件树），非常适合单元测试。之前 10 轮的测试扩展覆盖了组件层和视图层，现在是时候覆盖基础设施层了。

## Goals / Non-Goals

**Goals:**
- 为 Router 添加导航守卫和路由配置的测试
- 为 Permission 和 ClickOutside 指令添加行为测试
- 为 element-plus 和 vue-i18n 插件添加初始化测试
- 所有测试遵循代码库现有的测试风格（vitest + happy-dom + shallowMount 模式）

**Non-Goals:**
- 不修改任何生产代码
- 不新增依赖
- 不涉及后端、打包或部署变更

## Decisions

### 测试框架和工具
- 使用 vitest（代码库已有） + happy-dom 环境
- 对于 Plugin 测试，验证 `app.use()` 被正确调用，使用 `install` 函数的 spy
- 对于 Directive 测试，使用 `mount`/`shallowMount` 挂载测试元素并验证指令行为
- 对于 Router 测试，使用 `createRouter` 创建测试实例，`mockNavigator`/`router.push` 验证导航行为

### Mock 策略
- Router 测试需要 mock `@/store/modules/user` 和 `@/store/modules/embedded`（导航守卫依赖的 store）
- Directive 测试需要 mock `@/store/modules/permission`（权限校验依赖）
- Plugin 测试需要 mock `@/store/modules/locale`（i18n 依赖 locale store）
- 复用之前轮次验证过的 mock 模式（`vi.mock` 顶层调用 + `vi.hoisted` 工厂函数）

### 文件组织
- 每个模块的测试放在其目录下的 `__tests__/`：`src/router/__tests__/`, `src/directive/__tests__/`, `src/plugins/__tests__/`
- 遵循代码库约定：每个测试文件对应一个源文件，`*.test.ts` 扩展名

## Risks / Trade-offs

- **[Import chain error]** Plugin 测试可能因 vue-i18n 导入链触发 `service.ts`/`hmac.ts` 等问题 → 使用 `vi.mock` 在顶层 mock `@/config/axios/service`（已在前 10 轮验证有效）
- **[Pinia not initialized]** Router 测试中导航守卫依赖 Pinia store → 使用 `setActivePinia(createPinia())` 在 `beforeEach` 中初始化
- **[Router mock complexity]** Vue Router 的类型和 mock 在 vitest 环境中可能较复杂 → 优先使用 `createRouter` + `mockNavigator` 模式，避免复杂的 push/replace mock
