## ADDED Requirements

### Requirement: Nginx 容器 SHALL serve 前端静态文件
Nginx 容器 SHALL 托管前端构建产物，处理所有非 API 路径的 HTTP 请求。

#### Scenario: 前端页面访问
- **WHEN** 用户通过浏览器访问 `http://{host}:{port}/`
- **THEN** Nginx SHALL 返回前端应用的 `index.html`
- **AND** 前端路由 SHALL 正确工作（Vue Router history 模式需 fallback 到 index.html）

#### Scenario: 前端静态资源访问
- **WHEN** 浏览器请求 JS、CSS、图片等静态资源
- **THEN** Nginx SHALL 直接返回对应文件，并设置适当的 Content-Type 和缓存头

### Requirement: Nginx 容器 SHALL 反向代理后端 API
Nginx SHALL 将 `/de2api/` 路径下的请求反向代理到后端 App 容器。

#### Scenario: API 请求代理
- **WHEN** 用户请求 `http://{host}:{port}/de2api/` 下的任意路径
- **THEN** Nginx SHALL 将请求代理到 `http://pydataease-app:8000/de2api/`
- **AND** 请求头、请求体 SHALL 完整透传
- **AND** 响应状态码和响应体 SHALL 完整返回

#### Scenario: WebSocket 代理
- **WHEN** 用户请求 `http://{host}:{port}/websocket` 并携带 `Upgrade: websocket` 头
- **THEN** Nginx SHALL 正确处理 WebSocket 升级握手
- **AND** WebSocket 连接 SHALL 代理到 `ws://pydataease-app:8000/websocket`

### Requirement: 前端构建 SHALL 通过多阶段 Dockerfile 完成
前端构建 SHALL 在 Docker 构建阶段完成，运行时镜像 SHALL NOT 包含 Node.js 工具链。

#### Scenario: Dockerfile.nginx 多阶段构建
- **WHEN** 执行 `docker build -f Dockerfile.nginx .`
- **THEN** Stage 1 SHALL 使用 `node:18-slim` 执行 `npm ci` 和 `npm run build:distributed`
- **AND** Stage 2 SHALL 使用 `nginx:stable-alpine` 并仅 COPY 构建产物
- **AND** 运行时镜像 SHALL NOT 包含 Node.js 或 npm

### Requirement: Nginx 容器 SHALL 只暴露 HTTP 端口
Nginx 容器 SHALL 只对外暴露一个 HTTP 端口（默认 80，通过 Compose 映射到宿主机的 `DE_PORT`），后端 App 和 PG 容器 SHALL NOT 对外暴露端口。

#### Scenario: 端口映射
- **WHEN** `DE_PORT=8100` 配置在 `install.env` 中
- **THEN** `docker-compose.yml` SHALL 将宿主机 `8100` 映射到 Nginx 容器的 `80` 端口
- **AND** pydataease-app 的 `8000` 端口 SHALL NOT 映射到宿主机
- **AND** pydataease-pg 的 `5432` 端口 SHALL NOT 映射到宿主机（builtin 模式）
