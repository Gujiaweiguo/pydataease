# T01 Scope Freeze — FastAPI Backend Rewrite Baseline

Date: 2026-05-10  
Source baseline: `sdk/api/`, `core/core-frontend/src/api/`, `sdk/common/src/main/java/io/dataease/auth/`, `core/core-backend/src/main/resources/application*.yml`, `installer/`, `Dockerfile`

## Compatibility Matrix

| Dimension | Current Baseline | Target Strategy | Default Conclusion |
|---|---|---|---|
| HTTP API | Backend contract is defined by `sdk/api/**/*Api.java`; frontend calls hard-coded paths from `core/core-frontend/src/api/**/*.ts`; runtime path prefix is `/de2api` via `sdk/common/src/main/java/io/dataease/auth/interceptor/CorsConfig.java`. | Reproduce first-delivery standalone/community HTTP contract in FastAPI with path-level parity for migrated domains. | Must preserve path/method compatibility for first-delivery APIs. |
| Auth Headers | Header constants live in `sdk/common/src/main/java/io/dataease/constant/AuthConstant.java`: `X-DE-TOKEN`, `X-DE-LINK-TOKEN`, `X-EMBEDDED-TOKEN`, `X-DE-ASK-TOKEN`, `DE-GATEWAY-FLAG`, `DE-FORBIDDEN-FLAG`, `X-Userinfo`, `X-CAS-USER`, `Authorization`. | Preserve token headers and response flags used by core flows; enterprise gateway-only headers are boundary-only. | Core token/header semantics are must-migrate; enterprise gateway behavior is deferred/excluded. |
| Result Wrapper | Spring responses are globally wrapped by `ResultResponseBodyAdvice` (repo context) into the frontend-expected envelope. | Add FastAPI response envelope matching current wrapper semantics. | Must emulate wrapper behavior. |
| WebSocket | Frontend uses SockJS/STOMP at `/websocket?userId=` in `core/core-frontend/src/websocket/index.ts`; OSS backend exposes only `sdk/common/src/main/java/io/dataease/websocket/WsService.java` and `WsMessage.java`; full implementation is enterprise-boundary/de-xpack dependent. | Freeze boundary now; do not promise full STOMP broker parity in first delivery. | Deferred. |
| Background Tasks | Sync/task APIs live in `sdk/api/api-sync/**`; installer includes `installer/dataease/docker-compose-task.yml`; current system uses separate task runtime. | Preserve only HTTP compatibility needed by core flows; defer scheduler/sidecar parity. | Deferred. |
| Database | `application-standalone.yml` uses MySQL + Flyway `db/migration`; `application-desktop.yml` uses H2; distributed profile disables Flyway. | First delivery targets standalone MySQL semantics only. | Standalone/MySQL only. |
| Installer | `Dockerfile`, `installer/dectl`, `installer/dataease/docker-compose*.yml`, `installer/install.sh` define current runtime topology. | Preserve single app + MySQL deployment assumptions only. | Core standalone deployment only. |
| distributed/Nacos | `core/core-backend/src/main/resources/application-distributed.yml` enables Nacos/distributed mode and disables Flyway. | Do not migrate in first delivery. | Excluded. |
| desktop/H2 | `core/core-backend/src/main/resources/application-desktop.yml` uses H2 + desktop migrations. | Do not migrate in first delivery. | Excluded. |
| xpack/enterprise | Enterprise APIs live in `sdk/api/api-base/src/main/java/io/dataease/api/xpack/**`, `@XpackResource` APIs, frontend plugin loader, and `de-xpack/`. | Freeze interface boundaries only; no parity commitment. | Excluded from must-migrate. |

## Must Migrate (First Delivery)

First delivery is frozen to **standalone/community-oriented HTTP backend parity**.

### 1. Login and bootstrap
- Backend Java paths:
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/login/api/LoginApi.java`
  - `sdk/common/src/main/java/io/dataease/auth/filter/TokenFilter.java`
  - `sdk/common/src/main/java/io/dataease/auth/filter/FilterConfig.java`
  - `sdk/common/src/main/java/io/dataease/auth/interceptor/CorsConfig.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/login.ts`
  - `core/core-frontend/src/api/common.ts`
  - `core/core-frontend/src/api/setting/sysParameter.ts`
- Reason: entry/login/refresh/logout/UI bootstrap is mandatory.

### 2. User, org, role, permission core
- Backend Java paths:
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/user/api/UserApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/org/api/OrgApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/role/api/RoleApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/auth/api/AuthApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/apikey/api/ApiKeyApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/variable/api/SysVariablesApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/dataset/api/RowPermissionsApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/dataset/api/ColumnPermissionsApi.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/user.ts`
  - `core/core-frontend/src/api/auth.ts`
  - `core/core-frontend/src/api/org.ts`
  - `core/core-frontend/src/api/variable.ts`
- Reason: required for authenticated operation, RBAC, org switching, and dataset permissions.

### 3. Datasource core
- Backend Java paths:
  - `sdk/api/api-base/src/main/java/io/dataease/api/ds/DatasourceApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/ds/EngineApi.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/datasource.ts`
- Reason: foundational BI setup flow.

### 4. Dataset core
- Backend Java paths:
  - `sdk/api/api-base/src/main/java/io/dataease/api/dataset/DatasetTreeApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/dataset/DatasetTableApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/dataset/DatasetDataApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/dataset/DatasetTableSqlLogApi.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/dataset.ts`
- Reason: dataset CRUD, preview, field operations, and export entrypoints are core scope.

### 5. Chart core
- Backend Java paths:
  - `sdk/api/api-base/src/main/java/io/dataease/api/chart/ChartDataApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/chart/ChartViewApi.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/chart.ts`
- Reason: chart data and chart configuration are core BI rendering paths.

### 6. Visualization/dashboard core
- Backend Java paths:
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/DataVisualizationApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationSubjectApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationStoreApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationLinkageApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationLinkJumpApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationOuterParamsApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationWatermarkApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/VisualizationBackgroundApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/visualization/StaticResourceApi.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/visualization/dataVisualization.ts`
  - `core/core-frontend/src/api/visualization/linkage.ts`
  - `core/core-frontend/src/api/visualization/linkJump.ts`
  - `core/core-frontend/src/api/visualization/outerParams.ts`
  - `core/core-frontend/src/api/visualization/visualizationBackground.ts`
  - `core/core-frontend/src/api/watermark.ts`
  - `core/core-frontend/src/api/staticResource.ts`
- Reason: panel/dashboard lifecycle is the core product surface.

### 7. Template, map, font, menu, system settings needed by core UI
- Backend Java paths:
  - `sdk/api/api-base/src/main/java/io/dataease/api/template/TemplateManageApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/template/TemplateMarketApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/map/MapApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/map/GeoApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/map/CustomGeoApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/font/api/FontApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/menu/MenuApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/system/SysParameterApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/email/EmailApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/msgCenter/MsgCenterApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/license/LicenseApi.java`
- Frontend TS paths:
  - `core/core-frontend/src/api/template.ts`
  - `core/core-frontend/src/api/templateMarket.ts`
  - `core/core-frontend/src/api/map.ts`
  - `core/core-frontend/src/api/font.ts`
  - `core/core-frontend/src/api/common.ts`
  - `core/core-frontend/src/api/setting/sysParameter.ts`
  - `core/core-frontend/src/api/msg.ts`
  - `core/core-frontend/src/api/about.ts`
- Reason: needed for a usable standalone UI shell.

### 8. Export center HTTP contract
- Backend Java paths:
  - `sdk/api/api-base/src/main/java/io/dataease/api/exportCenter/ExportCenterApi.java`
  - `sdk/api/api-base/src/main/java/io/dataease/api/export/BaseExportApi.java` (non-HTTP boundary)
- Frontend TS paths:
  - `core/core-frontend/src/api/dataset.ts`
- Reason: frontend directly invokes export tasks/download/retry/delete flows.

## Deferred

- **WebSocket/STOMP notifications**
  - Frontend: `core/core-frontend/src/websocket/index.ts`, `core/core-frontend/src/pages/index/main.ts`
  - Backend boundary: `sdk/common/src/main/java/io/dataease/websocket/WsService.java`, `sdk/common/src/main/java/io/dataease/websocket/WsMessage.java`
  - Reason: boundary exists, but first delivery does not require broker parity.

- **Sync/task runtime and scheduler parity**
  - Backend: `sdk/api/api-sync/src/main/java/io/dataease/api/sync/task/api/TaskApi.java`, `TaskLogApi.java`, `sdk/api/api-sync/src/main/java/io/dataease/api/sync/datasource/api/SyncDatasourceApi.java`, `sdk/api/api-sync/src/main/java/io/dataease/api/sync/summary/api/SummaryApi.java`
  - Frontend: `core/core-frontend/src/api/sync/syncTask.ts`, `syncTaskLog.ts`, `syncSummary.ts`, `syncDatasource.ts`
  - Runtime: `installer/dataease/docker-compose-task.yml`
  - Reason: separate runtime plane, not required for first core BI delivery.

- **Operations/report/log/webhook/threshold flows**
  - Backend: `sdk/api/api-base/src/main/java/io/dataease/api/report/ReportApi.java`, `sdk/api/api-base/src/main/java/io/dataease/api/log/LogApi.java`, `sdk/api/api-base/src/main/java/io/dataease/api/threshold/ThresholdApi.java`, `sdk/api/api-base/src/main/java/io/dataease/api/webhook/WebhookApi.java`
  - Reason: useful but not required for baseline standalone migration acceptance.

- **AI / SQLBot / copilot helpers**
  - Backend: `sdk/api/api-base/src/main/java/io/dataease/api/ai/AiComponentApi.java`, `sdk/api/api-base/src/main/java/io/dataease/api/dataset/DataAssistantApi.java`
  - Frontend: `core/core-frontend/src/api/aiSqlBot.ts`, `core/core-frontend/src/api/aiComponent.ts`, copilot-related calls inside `core/core-frontend/src/api/dataset.ts`
  - Reason: additive capability, not baseline blocker.

- **Relation/lineage/internal-only boundaries**
  - Backend: `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/relation/api/RelationApi.java`, `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/auth/api/ResourceAuthApi.java`, `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/dataset/api/RowColPermissionApi.java`
  - Frontend: `core/core-frontend/src/api/relation/index.ts`
  - Reason: frozen for reference, not first-delivery gate.

## Excluded

- **desktop/H2 profile parity**
  - `core/core-backend/src/main/resources/application-desktop.yml`
  - `core/core-backend/src/main/resources/db/desktop`
- **distributed/Nacos profile parity**
  - `core/core-backend/src/main/resources/application-distributed.yml`
  - `installer/dataease/docker-compose-apisix.yml`
  - `installer/dataease/docker-compose-task.yml`
- **Unapproved xpack/enterprise parity**
  - `sdk/api/api-base/src/main/java/io/dataease/api/xpack/**`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/setting/api/PerSettingApi.java`
  - `sdk/api/api-permissions/src/main/java/io/dataease/api/permissions/embedded/api/EmbeddedApi.java`
  - `core/core-frontend/src/api/plugin.ts`
  - `core/core-frontend/src/components/plugin/src/ImportXpackTool.ts`
  - `de-xpack/`

## API Endpoint Inventory Summary

| Domain | Endpoint Count | Primary Backend Paths |
|---|---:|---|
| login | 7 | `sdk/api/api-permissions/.../LoginApi.java` |
| datasource | 36 | `sdk/api/api-base/.../DatasourceApi.java`, `EngineApi.java` |
| dataset | 38 | `sdk/api/api-base/.../DatasetTreeApi.java`, `DatasetTableApi.java`, `DatasetDataApi.java`, `DatasetTableSqlLogApi.java`, plus dataset permission APIs |
| chart | 15 | `sdk/api/api-base/.../ChartDataApi.java`, `ChartViewApi.java` |
| visualization | 56 | `sdk/api/api-base/.../visualization/*.java` |
| share | 16 | `sdk/api/api-base/.../xpack/share/*.java` |
| export | 9 | `sdk/api/api-base/.../ExportCenterApi.java` |
| system | 79 | `sdk/api/api-base/.../system`, `email`, `msgCenter`, `communicate`, `webhook`, IM integrations |
| template | 18 | `sdk/api/api-base/.../template/*.java` |
| map | 11 | `sdk/api/api-base/.../map/*.java` |
| font | 8 | `sdk/api/api-base/.../font/api/FontApi.java` |
| menu | 1 | `sdk/api/api-base/.../menu/MenuApi.java` |
| ai | 3 | `sdk/api/api-base/.../ai/AiComponentApi.java`, `.../dataset/DataAssistantApi.java` |
| license | 4 | `sdk/api/api-base/.../license/LicenseApi.java` |
| operation | 26 | `sdk/api/api-base/.../report/ReportApi.java`, `.../log/LogApi.java`, `.../threshold/ThresholdApi.java` |
| websocket | 0 HTTP APIs + 1 SockJS/STOMP boundary | `sdk/common/src/main/java/io/dataease/websocket/WsService.java`, `core/core-frontend/src/websocket/index.ts` |
| sync | 41 | `sdk/api/api-sync/**/*.java` |
| auth/permissions | 154 | `sdk/api/api-permissions/**/*.java` |

## Auth Pipeline Summary

### Header names
- `X-DE-TOKEN`
- `X-DE-LINK-TOKEN`
- `X-EMBEDDED-TOKEN`
- `X-DE-ASK-TOKEN`
- `DE-GATEWAY-FLAG`
- `DE-FORBIDDEN-FLAG`
- `X-Userinfo`
- `X-CAS-USER`
- `Authorization`

Source: `sdk/common/src/main/java/io/dataease/constant/AuthConstant.java`

### Filter chain order
1. `sdk/common/src/main/java/io/dataease/auth/filter/TokenFilter.java`
2. `sdk/common/src/main/java/io/dataease/auth/filter/CommunityTokenFilter.java`
3. CORS/path-prefix layer in `sdk/common/src/main/java/io/dataease/auth/interceptor/CorsConfig.java`

Registration source: `sdk/common/src/main/java/io/dataease/auth/filter/FilterConfig.java`

### Token types / identity modes
- Primary user JWT via `X-DE-TOKEN`
- Share/link JWT via `X-DE-LINK-TOKEN`
- Embedded token boundary via `X-EMBEDDED-TOKEN`
- Community-mode HMAC verification via `CommunityTokenFilter`
- Desktop bypass exists in `TokenFilter`, but desktop mode is excluded from first delivery

### Whitelist route categories
- Login/bootstrap: `/login/localLogin`, `/login/platformLogin/*`, `/login/modifyInvalidPwd`, `/dekey`, `/symmetricKey`, `/model`, `/sysParameter/defaultSettings`, `/sysParameter/ui`, `/sysParameter/defaultLogin`, `/sysParameter/requestTimeOut`, `/sysParameter/i18nOptions`
- Static/resources: `/static-resource/*`, `/map/*`, `/geo/*`, `/customGeo/*`, `/typeface/download`, `/typeface/defaultFont`, `/typeface/listFont`, `/communicate/down/*`, `/communicate/image/*`, static suffixes such as `.js`, `.css`, `.png`, `.svg`, `.woff2`
- Share/embed/ws: `/embedded/initIframe`, `/share/proxyInfo`, `/websocket`, `/mfa/qr/*`, `/mfa/login`
- Enterprise/gateway-adjacent entries also present: `/xpackComponent/content*`, `/oauth2/*`, `/saml/*`, IM qr/token routes, `/xpackModel`

## Runtime Topology Summary

### Current baseline
- `Dockerfile` packages backend app and exposes port `8100`.
- `installer/dectl` is the operational control script.
- Compose/runtime files:
  - `installer/dataease/docker-compose.yml` — main app
  - `installer/dataease/docker-compose-mysql.yml` — bundled MySQL
  - `installer/dataease/docker-compose-apisix.yml` — APISIX + etcd
  - `installer/dataease/docker-compose-task.yml` — sync-task-actuator
  - `installer/dataease/docker-compose-playwright.yml` — Playwright sidecar
- Runtime template: `installer/dataease/templates/application.yml`

### Current profile split
- `core/core-backend/src/main/resources/application.yml` — shared baseline, port `8100`
- `core/core-backend/src/main/resources/application-standalone.yml` — MySQL + Flyway `db/migration`
- `core/core-backend/src/main/resources/application-distributed.yml` — Nacos/distributed mode, Flyway disabled
- `core/core-backend/src/main/resources/application-desktop.yml` — H2 + `db/desktop`

### Frozen target
- **Development target:** FastAPI backend reproducing standalone/community backend contract against standalone DB semantics.
- **Production target:** single-service FastAPI app plus MySQL-compatible deployment shape for first delivery.

### Default conclusion
- T01 freezes first delivery to **standalone core app + MySQL + frontend contract parity**, not desktop/distributed/xpack runtime parity.
