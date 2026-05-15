## Capability: sql-execution-engine

Executes read-only SQL queries with validation and safety guards.

### Requirements

#### Requirement: Only SELECT and WITH queries SHALL be accepted
The SQL executor SHALL reject any query that does not begin with `SELECT` or `WITH` (case-insensitive, after stripping leading whitespace and trailing semicolons).

##### Scenario: User submits a valid SELECT query
- **WHEN** `execute_select("SELECT * FROM users")` is called
- **THEN** the query SHALL execute and return results

##### Scenario: User submits a WITH (CTE) query
- **WHEN** `execute_select("WITH cte AS (SELECT 1) SELECT * FROM cte")` is called
- **THEN** the query SHALL execute and return results

##### Scenario: User submits an INSERT query
- **WHEN** `execute_select("INSERT INTO users VALUES (1)")` is called
- **THEN** the executor SHALL raise HTTP 400 with detail "Only SELECT queries are allowed"

#### Requirement: Dangerous SQL keywords SHALL be rejected
After sanitizing comments and quoted strings, the executor SHALL reject queries containing any of: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`, `REVOKE`, `MERGE`, `CALL`, `COPY`, `VACUUM`, `ANALYZE`, `COMMENT`, `EXECUTE`.

##### Scenario: User hides DROP in a comment
- **WHEN** `execute_select("SELECT 1 /* DROP TABLE users */")` is called
- **THEN** the executor SHALL strip the comment before checking and SHALL accept the query

##### Scenario: User attempts multi-statement injection
- **WHEN** `execute_select("SELECT 1; DROP TABLE users")` is called
- **THEN** the executor SHALL raise HTTP 400 with detail "Only a single SELECT query is allowed"

#### Requirement: Auto-LIMIT SHALL be applied when no LIMIT clause exists
The executor SHALL append `LIMIT {limit}` (default 1000) to queries that don't already contain a `LIMIT` keyword.

##### Scenario: Query has no LIMIT
- **WHEN** `execute_select("SELECT * FROM big_table")` is called
- **THEN** the executed SQL SHALL be `"SELECT * FROM big_table LIMIT 1000"`

##### Scenario: Query already has a LIMIT
- **WHEN** `execute_select("SELECT * FROM big_table LIMIT 50")` is called
- **THEN** the query SHALL execute as-is without appending another LIMIT

#### Requirement: Response SHALL include sql, data, fields, and total
The executor SHALL return a dict with the executed SQL string, row data as arrays, field metadata with name and type, and total row count.

##### Scenario: Query returns results
- **WHEN** a valid query returns 3 rows with columns `id` and `name`
- **THEN** the response SHALL be `{"sql": "...", "data": [[...], [...], [...]], "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "varchar"}], "total": 3}`

#### Requirement: SQL errors SHALL return HTTP 400
Database execution errors SHALL be caught and returned as HTTP 400 responses.

##### Scenario: Query references a non-existent table
- **WHEN** `execute_select("SELECT * FROM nonexistent")` is called
- **THEN** the executor SHALL raise HTTP 400 with detail starting with "SQL preview failed:"
