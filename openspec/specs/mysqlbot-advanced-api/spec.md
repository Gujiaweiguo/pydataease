## ADDED Requirements

### Requirement: MySQLBot advanced assistant callback API endpoints

The system SHALL provide REST API endpoints under the `/de2api/mysqlbot/api/` prefix for MySQLBot's advanced assistant to callback and retrieve datasource connection credentials. All endpoints SHALL require a valid API Key passed via the `X-API-Key` request header.

**Primary endpoint (used by MySQLBot):** MySQLBot's advanced assistant calls ONE endpoint (`GET /datasources`) to get a list of datasources with full database connection credentials. MySQLBot then connects directly to databases — it does NOT proxy queries through pydataease. The response format MUST match MySQLBot's `AssistantOutDsSchema` (`id`, `name`, `type`, `host`, `port`, `dataBase`, `user`, `password`, `extraParams`, `db_schema`, `tables`, etc.).

**Additional endpoints (bonus):** Tables, fields, and query endpoints are provided as a general-purpose database metadata API. They are NOT used by MySQLBot's advanced assistant flow but may be useful for other integrations.

#### Scenario: List datasources with full connection credentials

- **WHEN** a GET request is sent to `/de2api/mysqlbot/api/datasources` with a valid `X-API-Key` header
- **THEN** the system SHALL return a JSON array of datasource objects matching MySQLBot's `AssistantOutDsSchema`, each containing:
  - `id` (string) — datasource identifier
  - `name` (string) — display name
  - `type` (string) — database type (e.g. "mysql", "postgresql")
  - `host` (string) — database host address
  - `port` (string) — database port
  - `dataBase` (string) — database name
  - `user` (string) — database username
  - `password` (string) — database password
  - `extraParams` (string or null) — additional connection parameters
  - `db_schema` (string or null) — schema name if applicable
  - Only non-folder datasources that exist in the system SHALL be returned
  - Credentials are extracted from the `core_datasource.configuration` JSONB field, handling key variants (`dataBase`/`database`, `username`/`user`, `extraParams`/`extraParameters`)

#### Scenario: List datasources without API Key

- **WHEN** a GET request is sent to `/de2api/mysqlbot/api/datasources` without an `X-API-Key` header
- **THEN** the system SHALL return HTTP 401 with `{"code": 401, "data": null, "msg": "Missing API Key"}`

#### Scenario: List datasources with invalid API Key

- **WHEN** a GET request is sent to `/de2api/mysqlbot/api/datasources` with an `X-API-Key` header value that does not match the configured key
- **THEN** the system SHALL return HTTP 401 with `{"code": 401, "data": null, "msg": "Invalid API Key"}`

### Requirement: Table listing endpoint (bonus)

The system SHALL provide a GET endpoint at `/de2api/mysqlbot/api/datasources/{datasource_id}/tables` that returns all tables in the specified datasource.

#### Scenario: List tables for a valid datasource

- **WHEN** a GET request is sent to `/de2api/mysqlbot/api/datasources/{datasource_id}/tables` with a valid API Key and a valid datasource_id
- **THEN** the system SHALL return a JSON array of table objects, each containing `name` (string) and `schema` (string, if applicable)

#### Scenario: List tables for a non-existent datasource

- **WHEN** a GET request is sent with a valid API Key but a datasource_id that does not exist
- **THEN** the system SHALL return HTTP 404 with `{"code": 404, "data": null, "msg": "Datasource not found"}`

### Requirement: Field metadata endpoint (bonus)

The system SHALL provide a GET endpoint at `/de2api/mysqlbot/api/datasources/{datasource_id}/tables/{table_name}/fields` that returns column metadata for the specified table.

#### Scenario: List fields for a valid table

- **WHEN** a GET request is sent with a valid API Key, a valid datasource_id, and a valid table_name
- **THEN** the system SHALL return a JSON array of field objects, each containing `name` (string), `type` (string, the raw database type), `nullable` (boolean), and `comment` (string or null)

#### Scenario: List fields for a non-existent table

- **WHEN** a GET request is sent with a valid API Key but a table_name that does not exist in the datasource
- **THEN** the system SHALL return HTTP 404 with `{"code": 404, "data": null, "msg": "Table not found"}`

### Requirement: SQL query execution endpoint (bonus)

The system SHALL provide a POST endpoint at `/de2api/mysqlbot/api/datasources/{datasource_id}/query` that executes a read-only SQL statement against the specified datasource and returns structured results.

#### Scenario: Execute a valid SELECT query

- **WHEN** a POST request is sent with a valid API Key, a valid datasource_id, and a JSON body `{"sql": "SELECT * FROM some_table LIMIT 10"}`
- **THEN** the system SHALL validate the SQL is read-only (SELECT only, no INSERT/UPDATE/DELETE/DROP), apply a row limit if none is present, execute the query, and return `{"fields": [...], "data": [[...], ...], "total": <int>}`

#### Scenario: Reject a write query

- **WHEN** a POST request is sent with `{"sql": "DROP TABLE users"}`
- **THEN** the system SHALL return HTTP 400 with `{"code": 400, "data": null, "msg": "Only SELECT queries are allowed"}`

#### Scenario: Reject a multi-statement query

- **WHEN** a POST request is sent with `{"sql": "SELECT 1; DROP TABLE users"}`
- **THEN** the system SHALL return HTTP 400 with `{"code": 400, "data": null, "msg": "Only SELECT queries are allowed"}`

#### Scenario: Execute query on non-existent datasource

- **WHEN** a POST request is sent with a valid API Key but a datasource_id that does not exist
- **THEN** the system SHALL return HTTP 404 with `{"code": 404, "data": null, "msg": "Datasource not found"}`

#### Scenario: Execute query with missing SQL

- **WHEN** a POST request is sent with an empty JSON body or no `sql` field
- **THEN** the system SHALL return HTTP 422 with a validation error message
