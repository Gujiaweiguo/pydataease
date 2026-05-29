## ADDED Requirements

### Requirement: First-wave external SQL datasource support SHALL include PostgreSQL and MySQL
The MVP datasource layer SHALL support PostgreSQL and MySQL as the required first-wave external SQL datasource types.

#### Scenario: User opens the supported datasource type list for SQL connectivity
- **WHEN** the first-wave datasource feature is presented for external SQL connections
- **THEN** PostgreSQL and MySQL SHALL be available as supported datasource types

#### Scenario: User attempts to configure a deferred datasource type
- **WHEN** a first-wave deployment receives a request for Oracle, SQL Server, ClickHouse, Trino/Presto, Hive, Spark, MongoDB, Elasticsearch, Redis, API datasource, or cloud-warehouse long-tail support
- **THEN** the system SHALL treat that datasource type as out of scope for the MVP rather than pretending it is supported

### Requirement: Supported SQL datasources SHALL support create and test connection flows
The MVP datasource contract SHALL allow users to create datasource definitions and validate connectivity before the datasource is used downstream.

#### Scenario: User submits valid PostgreSQL datasource settings
- **WHEN** the user creates or tests a PostgreSQL datasource with valid connection parameters
- **THEN** the system SHALL report the connection as successful

#### Scenario: User submits valid MySQL datasource settings
- **WHEN** the user creates or tests a MySQL datasource with valid connection parameters
- **THEN** the system SHALL report the connection as successful

#### Scenario: User submits invalid datasource settings
- **WHEN** the user tests a supported datasource with invalid host, port, credentials, or database settings
- **THEN** the system SHALL return a connection failure result without marking the datasource as valid

### Requirement: Supported SQL datasources SHALL expose metadata needed for dataset authoring
The MVP datasource contract SHALL expose metadata introspection for configured SQL datasources so users can browse available structures before building datasets.

#### Scenario: User browses PostgreSQL metadata
- **WHEN** the user inspects a configured PostgreSQL datasource
- **THEN** the system SHALL return available databases, schemas, tables, and columns as applicable to the datasource model

#### Scenario: User browses MySQL metadata
- **WHEN** the user inspects a configured MySQL datasource
- **THEN** the system SHALL return available databases, tables, and columns as applicable to the datasource model

### Requirement: Supported SQL datasources SHALL provide read-only query preview for dataset authoring
The MVP datasource contract SHALL support read-only query preview against configured SQL datasources so users can validate dataset logic before publishing downstream.

#### Scenario: User previews a query against a supported datasource
- **WHEN** the user submits a valid read-only preview query against a configured PostgreSQL or MySQL datasource
- **THEN** the system SHALL return preview rows and field metadata from that datasource

### Requirement: First-wave datasource success SHALL include downstream dataset consumption
The MVP SHALL be considered complete only when datasets built from supported first-wave datasources can be consumed by downstream chart and dashboard flows.

#### Scenario: Dataset created from a supported datasource is used downstream
- **WHEN** a dataset is authored from a PostgreSQL or MySQL datasource and saved successfully
- **THEN** downstream chart or dashboard flows SHALL be able to consume that dataset through the existing BI path
