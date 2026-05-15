## 1. Wave 1 — 定格与基线

- [x] 1.1 T01 范围定格与兼容矩阵冻结
  - 依赖: 无
  - 风险: High
  - 输入: 本计划文件；`sdk/api/**/*Api.java`；`core/core-frontend/src/api/*.ts`；`installer/` 现有运行拓扑
  - 输出: 范围冻结清单、兼容矩阵快照、默认排除项清单、首批必须迁移模块清单
  - 验收标准:
    - 生成兼容矩阵快照，覆盖 API / Auth / WebSocket / DB / Installer / Profiles 六个维度以上
    - 生成首批迁移范围清单，明确“必须迁移 / 延后迁移 / 非目标”三类
    - 执行者后续任务不再需要自行决定“是否支持 desktop/distributed”
  - 回滚方案:
    - 删除未批准的范围扩展清单，恢复到 Plan v1 默认边界
    - 若兼容矩阵定义错误，以 T01 产物为唯一修订入口，不在后续任务中补丁式修正

- [x] 1.2 T02 契约清点与刻画测试基线生成
  - 依赖: T01
  - 风险: High
  - 输入: `sdk/api/**/*Api.java`；`core/core-frontend/src/api/*.ts`；现有 Java 响应包装、认证头、错误码实现
  - 输出: API inventory；契约刻画测试清单；关键 HTTP/认证/错误行为快照
  - 验收标准:
    - 产出端点 inventory，至少覆盖前端 API 模块中的关键域
    - characterization tests 可独立运行，并在当前 Java 服务或契约 mock 上通过
    - inventory 中每个关键域至少含 1 个成功路径与 1 个失败路径断言
  - 回滚方案:
    - 若 inventory 与前端真实调用不一致，回滚到最近一次完整 inventory 快照，重新从前端调用源生成
    - 若 characterization tests 过于脆弱，保留 inventory，重写测试而不推进功能迁移

- [x] 1.3 T03 FastAPI + uv 工程骨架初始化
  - 依赖: T01
  - 风险: Medium
  - 输入: T01 范围冻结结果；FastAPI / uv / SQLAlchemy / Alembic 官方指导
  - 输出: 新 Python 工程骨架；`pyproject.toml`；`uv.lock`；统一目录约定、运行入口、基础 lint/test 命令
  - 验收标准:
    - `uv sync` 成功且生成锁文件
    - `uv run fastapi run app/main.py --help` 或等价入口可执行
    - `uv run pytest` 可在空业务状态下跑通基础测试骨架
  - 回滚方案:
    - 若目录命名或依赖方案错误，保留 characterization tests，删除新骨架并重新初始化，不污染旧 Java 后端

## 2. Wave 2 — 核心基础设施

- [ ] 2.1 T04 PostgreSQL schema 建模与 Alembic 基线迁移
  - 依赖: T02, T03
  - 风险: Critical
  - 输入: 现有 MySQL/H2 结构事实；T02 契约；T03 工程骨架
  - 输出: PostgreSQL 目标 schema；SQLAlchemy 模型；Alembic baseline 与增量迁移脚本
  - 验收标准:
    - PostgreSQL 空库可通过 Alembic 初始化到 head
    - 至少一套代表性历史数据可从导出样本迁入 PostgreSQL 并通过约束校验
    - 关键表（datasource/dataset/chart/visualization/share/export）均有模型与迁移覆盖
  - 回滚方案:
    - 回滚到最近一个 Alembic revision，重建测试库
    - 对生产演练环境使用数据库快照/pg_dump 回退，不允许手工删表修正

- [ ] 2.2 T05 配置体系、环境分层与本地/生产运行编排
  - 依赖: T03
  - 风险: High
  - 输入: T03 工程骨架；`application*.yml`；`installer/install.conf`
  - 输出: Pydantic settings / env 文件模板；开发环境运行方式；生产环境运行方式；Docker / compose 基础编排
  - 验收标准:
    - `uv run` 本地启动支持 dev 配置且可连 Docker PostgreSQL
    - `docker compose` 生产编排可启动 `pydataease-app` 与 `pydataease-pg`
    - 所有敏感配置改为环境变量注入，不依赖硬编码
  - 回滚方案:
    - 回退 compose 与 env 模板到上一稳定版本
    - 如生产编排不稳定，恢复旧 Java compose，不影响数据库快照

- [ ] 2.3 T06 认证、响应包装与请求中间件兼容层
  - 依赖: T02, T03
  - 风险: Critical
  - 输入: T02 契约测试；当前认证过滤链与 header 语义；T03/T05 基础设施
  - 输出: FastAPI 中间件/依赖认证层；统一响应包装；白名单、分享 token、嵌入 token、错误码兼容策略
  - 验收标准:
    - characterization tests 中与鉴权相关的成功/失败场景全部通过
    - 白名单接口无需认证即可访问；受保护接口在缺 token / 坏 token / 过期 token 时返回兼容错误
    - 分享/嵌入链路至少具备明确兼容实现或显式拒绝策略并被测试覆盖
  - 回滚方案:
    - 如新认证层导致大面积契约失败，回退到上一个通过 characterization tests 的中间件版本
    - 不修改前端重试逻辑作为临时补救

## 3. Wave 3 — 业务替代切片

- [ ] 3.1 T07 数据源、SQL 执行引擎与仓储抽象替代
  - 依赖: T04, T05
  - 风险: Critical
  - 输入: T04 PostgreSQL 模型；当前 datasource / engine / Calcite 相关实现；T05/T06 基础设施
  - 输出: Python 数据访问层与仓储抽象；数据源管理接口替代；SQL 执行、预览、连接校验的可运行方案
  - 验收标准:
    - 数据源 CRUD 与连接校验 API 契约通过
    - 至少支持 PostgreSQL 作为首批主数据库，并对现有业务必须的数据访问路径可执行
    - 代表性 SQL 预览/执行用例通过 characterization / integration tests
  - 回滚方案:
    - 若执行引擎替代失败，回退到上一稳定仓储抽象，并冻结高阶 SQL 能力在 backlog，而不是污染基础 CRUD

- [ ] 3.2 T08 数据集、字段与权限相关接口替代
  - 依赖: T04, T05, T06, T07
  - 风险: High
  - 输入: T06 认证层；T07 数据访问基础；当前 dataset / permission 管理逻辑
  - 输出: 数据集树、字段、SQL 预览、权限相关 FastAPI 接口；对应测试与样例数据
  - 验收标准:
    - 数据集树、字段、预览、权限校验契约测试通过
    - 至少 1 套真实数据集样例从创建到查询全流程通过
    - 越权访问失败路径被自动化验证
  - 回滚方案:
    - 回退数据集相关路由/服务到上一通过版本；保留 schema 但撤销路由挂载

- [ ] 3.3 T09 图表与可视化核心接口替代
  - 依赖: T04, T05, T06, T07, T08
  - 风险: Critical
  - 输入: T07/T08 完成的查询与数据集基础；当前 chart / visualization / linkage / template 相关逻辑
  - 输出: 图表数据查询接口；可视化 CRUD、联动、跳转、外部参数等核心接口；关键 UI smoke 验证
  - 验收标准:
    - 图表与可视化关键契约测试通过
    - Playwright smoke 能完成登录后打开至少一个 dashboard 并拉取图表数据
    - 联动/外部参数至少各有 1 条成功路径与 1 条失败路径测试
  - 回滚方案:
    - 若图表/可视化兼容失败，保留底层查询层，回退路由切换；必要时临时保持 Java 服务提供该域接口直到下一切片完成

- [ ] 3.4 T10 分享、导出、系统参数与剩余核心接口收口
  - 依赖: T04, T05, T06, T07
  - 风险: Medium
  - 输入: T06 认证兼容层；T07-T09 主业务切片；当前 share/export/system/map/menu/font 等剩余接口
  - 输出: 分享、导出、系统参数、资源/菜单等剩余核心接口；剩余契约覆盖闭环
  - 验收标准:
    - inventory 中标记为首批必须支持的剩余接口全部有实现或明确拒绝策略
    - 分享与导出成功/失败路径自动化验证通过
    - `404/501` 仅出现在已登记的 deferred 接口上
  - 回滚方案:
    - 如某剩余接口导致系统不稳定，回退该接口切片，不回退已稳定核心域

## 4. Wave 4 — 运行时与交付

- [ ] 4.1 T11 定时任务、长任务执行链路与 worker 拓扑替代
  - 依赖: T05, T06, T07, T10
  - 风险: High
  - 输入: T07 执行引擎；T10 导出与同步任务需求；当前 Quartz / sync-task-actuator 拓扑
  - 输出: Python scheduler / worker 方案；长任务执行、重试、状态查询、幂等保障；生产可运行的任务拓扑
  - 验收标准:
    - 所有首批必须任务具有启动、执行、失败、重试、状态查询路径
    - 长任务不阻塞 web 请求线程
    - 至少 1 条失败重试与 1 条幂等保护测试通过
  - 回滚方案:
    - 若独立 worker 拓扑不稳定，回退到上一个稳定执行器版本；禁止将失败任务临时塞回 web 进程

- [ ] 4.2 T12 WebSocket、网关与安装/部署链路改造
  - 依赖: T05, T06, T09, T10, T11
  - 风险: Critical
  - 输入: T05 运行编排；T06 鉴权层；T09/T10/T11 业务与任务拓扑；`installer/dectl` / `install.sh` / APISIX 配置 / `Dockerfile`
  - 输出: 新 Dockerfile；新/改 compose 文件；installer / dectl / healthcheck 改造；WebSocket / 网关兼容实现或显式降级路径
  - 验收标准:
    - `pydataease-app` 与 `pydataease-pg` 生产拓扑可一键启动并通过健康检查
    - 安装/升级/停止/状态命令完成最小闭环演练
    - WebSocket 与网关相关首批需求被自动验证或明确标记不支持并阻止发布
  - 回滚方案:
    - 生产演练失败时，恢复旧 installer 与 Java 镜像链路；数据库保持快照隔离，不执行不可逆切换

- [ ] 4.3 T13 Cutover 预演、数据迁移演练与发布准备
  - 依赖: T04-T12
  - 风险: Critical
  - 输入: T04-T12 全部完成结果；历史数据样本；开发/生产准入标准
  - 输出: Cutover runbook；回滚 runbook；迁移演练记录；发布门禁结果
  - 验收标准:
    - 完整 cutover 演练成功并生成 runbook
    - 回滚演练成功且恢复到旧链路时间与步骤可量化
    - 所有关键测试集在 prod-like 环境通过
  - 回滚方案:
    - 本任务本身的回滚即执行既定 rollback runbook；若预演失败，禁止进入正式发布

## 5. Final Verification Wave

- [ ] 5.1 F1 Plan Compliance Audit — oracle
- [ ] 5.2 F2 Code Quality Review — unspecified-high
- [ ] 5.3 F3 Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] 5.4 F4 Scope Fidelity Check — deep
