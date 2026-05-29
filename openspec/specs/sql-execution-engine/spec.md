## MODIFIED Requirements

### Requirement: Only SELECT and WITH queries SHALL be accepted
For query preview requests targeting configured SQL datasources, the SQL executor SHALL reject any query that does not begin with `SELECT` or `WITH` (case-insensitive, after stripping leading whitespace and trailing semicolons).

#### Scenario: User submits a valid SELECT query
- **WHEN** `execute_select("SELECT * FROM users")` is called
- **THEN** the query SHALL execute and return results

#### Scenario: User submits a WITH (CTE) query
- **WHEN** `execute_select("WITH cte AS (SELECT 1) SELECT * FROM cte")` is called
- **THEN** the query SHALL execute and return results

#### Scenario: User submits an INSERT query
- **WHEN** `execute_select("INSERT INTO users VALUES (1)")` is called
- **THEN** the executor SHALL raise HTTP 400 with detail "Only SELECT queries are allowed"

#### Scenario: User previews a valid SELECT against a configured external datasource
- **WHEN** a preview request submits a valid `SELECT` query for a configured PostgreSQL or MySQL datasource
- **THEN** the executor SHALL accept the query for that datasource path

## ADDED Requirements

### Requirement: Query preview SHALL execute against the selected configured SQL datasource
The SQL execution engine SHALL run preview queries against the configured datasource selected for the request, rather than assuming only the internal runtime database path.

#### Scenario: User previews SQL against PostgreSQL datasource
- **WHEN** a preview request targets a configured PostgreSQL datasource
- **THEN** the execution engine SHALL run the query against that PostgreSQL datasource

#### Scenario: User previews SQL against MySQL datasource
- **WHEN** a preview request targets a configured MySQL datasource
- **THEN** the execution engine SHALL run the query against that MySQL datasource

#### Scenario: Preview request references an unknown datasource
- **WHEN** a preview request references a datasource that is missing, invalid, or unsupported by the first-wave scope
- **THEN** the execution engine SHALL reject the preview request with an explicit error instead of silently falling back to another datasource
