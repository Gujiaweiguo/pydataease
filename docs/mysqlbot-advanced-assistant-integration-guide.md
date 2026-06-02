# MySQLBot 高级小助手集成部署指南

## 概述

MySQLBot 高级小助手模式允许 MySQLBot 通过调用 pydataease 的回调 API 获取数据源连接凭证，然后由 MySQLBot 直接连接目标数据库执行查询。

工作流程：

1. MySQLBot 调用 pydataease API 获取可用数据源列表（含加密的连接信息）
2. MySQLBot 使用 AES 解密获取数据库连接凭证
3. MySQLBot 直连目标数据库，执行用户提问生成的 SQL 并返回结果

---

## 前提条件

| 条件 | 说明 |
|------|------|
| pydataease 已部署 | 后端服务正常运行，版本包含 MySQLBot 回调 API |
| MySQLBot 已部署 | MySQLBot 服务已安装并可访问 |
| 网络连通 | MySQLBot 能访问 pydataease 的公网地址 |
| 数据源已配置 | pydataease 中已添加至少一个数据源 |

---

## pydataease 侧配置

### 1. 进入设置页面

以管理员身份登录 pydataease，进入 **系统设置 → 第三方设置**，找到 MySQLBot 配置区域。

### 2. 填写基础信息

- **服务地址**：填写 MySQLBot 的服务 URL，格式 `https://your-mysqlbot-domain.com`
- **应用 ID**：填写 MySQLBot 中创建的应用 ID

### 3. 选择模式

选择 **高级小助手（Advanced）** 模式。选择后页面会显示额外的安全配置项。

### 4. 配置 API Key（必填）

在 **API Key** 输入框中填写一个自定义密钥。要求：

- 建议使用 32 位以上的随机字符串
- 此 Key 将用于 MySQLBot 调用 pydataease API 时的身份验证
- 请妥善保管，MySQLBot 侧需要配置相同的 Key

### 5. 配置 AES 加密（推荐）

AES 加密用于保护数据源连接凭证在传输过程中的安全。

- **AES Key**：填写 32 个字符的加密密钥（AES-256 要求 32 字节密钥）
- **AES IV**：填写 16 个字符的初始化向量。如果不填，默认使用内置值

加密算法为 AES-256-CBC，使用 PKCS7 填充，输出 Base64 编码的密文。

被加密的字段包括：`host`、`user`、`password`、`dataBase`、`db_schema`、`mode`。

### 6. 保存并验证

点击 **保存** 按钮。如需验证连通性，可点击 **验证** 按钮，系统会尝试访问 MySQLBot 的应用信息接口。

---

## MySQLBot 侧配置

### 1. 创建或编辑小助手

在 MySQLBot 管理后台创建一个新的小助手，或编辑已有小助手。

### 2. 配置 pydataease 连接

在数据源回调配置中填写以下信息：

- **Domain**：pydataease 的公网访问地址，例如 `https://your-pydataease-domain.com`
- **Endpoint Path**：`/de2api/mysqlbot/api/datasources`

### 3. 配置认证凭证

在凭证（Certificate）配置中添加 API Key 请求头：

```json
[{"target": "header", "key": "X-API-Key", "value": "<你的 API Key>"}]
```

将 `<你的 API Key>` 替换为 pydataease 侧配置的相同 API Key。

### 4. 配置 AES 解密（如 pydataease 侧启用了加密）

- **AES Key**：填写与 pydataease 侧完全相同的 32 字符密钥
- **AES IV**：填写与 pydataease 侧相同的 IV。如果 pydataease 侧未自定义 IV，此处可留空（使用默认值）
- **启用加密**：打开开关

> 两端的 AES Key 和 IV 必须完全一致，否则 MySQLBot 无法解密数据源凭证。

### 5. 保存并测试

保存配置后，在 MySQLBot 中测试小助手功能，确认能正常获取数据源列表。

---

## API 端点参考

所有端点均在 `/de2api` 前缀下，需要通过 `X-API-Key` 请求头认证。

### 获取数据源列表

```
GET /de2api/mysqlbot/api/datasources
```

返回 pydataease 中所有非文件夹类型的数据源，包含连接凭证（如启用 AES 则为密文）。

### 获取数据源的表列表

```
GET /de2api/mysqlbot/api/datasources/{datasource_id}/tables
```

返回指定数据源中的所有表。

### 获取表的字段列表

```
GET /de2api/mysqlbot/api/datasources/{datasource_id}/tables/{table_name}/fields
```

返回指定表的列元数据，包括列名、数据类型。

### 执行只读 SQL 查询

```
POST /de2api/mysqlbot/api/datasources/{datasource_id}/query
Content-Type: application/json

{"sql": "SELECT * FROM your_table LIMIT 10"}
```

在指定数据源上执行只读 SQL，最多返回 1000 行。

### 通用说明

| 项目 | 值 |
|------|-----|
| 认证方式 | `X-API-Key` 请求头 |
| 频率限制 | 每个端点 30 次/分钟 |
| 超限响应 | HTTP 429 |

---

## 安全说明

**API Key 认证**：所有回调端点通过 `X-API-Key` 请求头验证身份，使用常量时间比较防止时序攻击。

**AES-256-CBC 加密**：数据源的敏感连接信息在返回前经过 AES-256-CBC 加密和 Base64 编码，确保凭证在公网传输时的安全。

**频率限制**：每个端点限制 30 次请求/分钟，超出后返回 429 状态码。

**只读 SQL**：查询端点强制只读，不接受 INSERT、UPDATE、DELETE、DROP 等写操作语句，并自动添加行数上限（1000 行）。

**白名单机制**：回调 API 路径 `/mysqlbot/api/` 已加入系统白名单，不经过用户登录认证中间件，但每个请求都会校验 API Key。

---

## 故障排查

| 现象 | 可能原因 | 解决方法 |
|------|----------|----------|
| 返回 401 / Missing API Key | 请求未携带 `X-API-Key` 头 | 检查 MySQLBot 侧凭证配置，确认请求头名称为 `X-API-Key` |
| 返回 401 / Invalid API Key | 两端 API Key 不一致 | 核对 pydataease 和 MySQLBot 侧的 API Key 是否完全相同 |
| 数据源列表为空 | pydataease 中未配置数据源 | 在 pydataease 的数据源管理中添加至少一个数据源 |
| AES 解密失败 | 两端 Key 或 IV 不一致 | 逐一核对 AES Key 和 AES IV 是否完全相同，注意首尾空格 |
| AES 解密失败（版本问题） | 加密算法实现不一致 | 确认两端均使用 AES-256-CBC + PKCS7 填充 + Base64 输出 |
| 返回 429 | 请求频率超限 | 降低请求频率，每个端点上限 30 次/分钟 |
| 返回 404 / Datasource not found | 数据源 ID 不存在或已删除 | 确认使用的数据源 ID 是否正确 |
| 返回 400 / 只读相关错误 | SQL 包含写操作 | 仅允许 SELECT 语句 |
