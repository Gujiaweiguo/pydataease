## ADDED Requirements

### Requirement: Preview dataset data
The system SHALL provide a `POST /datasetData/previewData` endpoint that accepts a request body containing a dataset group ID and optional pagination parameters (limit, offset), resolves the dataset's base SQL from the associated dataset group and tables, executes the SQL against the appropriate datasource with pagination, and returns the result rows along with field metadata.

#### Scenario: Preview data for an existing dataset
- **WHEN** a POST request is sent to `/datasetData/previewData` with a valid dataset group ID in the body
- **THEN** the system resolves the dataset's base SQL, executes it with pagination (default limit from request), and returns an object containing the data rows and field definitions

#### Scenario: Preview data for a non-existent dataset
- **WHEN** a POST request is sent to `/datasetData/previewData` with a dataset group ID that does not exist
- **THEN** the system returns an HTTP 404 error with an appropriate message

### Requirement: Get enum values for a field
The system SHALL provide a `POST /datasetData/enumValue` endpoint that accepts a request body with field identification (dataset group ID and field name or field ID), builds a `SELECT DISTINCT` query for that field against the dataset's base SQL, executes it with a configurable result limit, and returns a flat list of distinct values.

#### Scenario: Get distinct values for a text field
- **WHEN** a POST request is sent to `/datasetData/enumValue` with a valid dataset group ID and field identifier
- **THEN** the system returns a list of distinct string values for that field, limited to the configured maximum

#### Scenario: Get distinct values for a numeric field
- **WHEN** a POST request is sent to `/datasetData/enumValue` with a valid dataset group ID and a numeric field identifier
- **THEN** the system returns a list of distinct numeric values for that field, limited to the configured maximum

### Requirement: Get enum value objects with metadata
The system SHALL provide a `POST /datasetData/enumValueObj` endpoint that accepts the same parameters as `enumValue` but returns objects containing both the value and associated metadata (text, value pairs) suitable for dropdown population.

#### Scenario: Get enum value objects for a filter field
- **WHEN** a POST request is sent to `/datasetData/enumValueObj` with a valid dataset group ID and field identifier
- **THEN** the system returns a list of objects, each containing at minimum a text label and a value property for the distinct field values

### Requirement: Get enum values from datasource directly
The system SHALL provide a `POST /datasetData/enumValueDs` endpoint that accepts a request body with datasource identification and table/column references, queries the datasource directly (bypassing dataset group SQL), and returns distinct values for the specified column.

#### Scenario: Get distinct values directly from a MySQL datasource
- **WHEN** a POST request is sent to `/datasetData/enumValueDs` with a valid datasource ID, table name, and column name
- **THEN** the system connects to the datasource, executes `SELECT DISTINCT <column> FROM <table>` with a limit, and returns the distinct values

#### Scenario: Datasource connection failure
- **WHEN** a POST request is sent to `/datasetData/enumValueDs` with a datasource ID that cannot be connected to
- **THEN** the system returns an HTTP 500 error with a message indicating the connection failure

### Requirement: Get field tree structure for dataset
The system SHALL provide a `POST /datasetData/getFieldTree` endpoint that accepts a dataset group ID, retrieves all fields for the dataset, and returns them organized in a tree structure grouped by field type or group type (dimension vs quota).

#### Scenario: Get field tree for a dataset with dimensions and quotas
- **WHEN** a POST request is sent to `/datasetData/getFieldTree` with a valid dataset group ID
- **THEN** the system returns a tree structure with top-level nodes for each field group type, containing child nodes for each field in that group

#### Scenario: Get field tree for a dataset with no fields
- **WHEN** a POST request is sent to `/datasetData/getFieldTree` for a dataset with no associated fields
- **THEN** the system returns an empty tree structure

### Requirement: Export dataset details from chart context
The system SHALL provide a `POST /datasetData/innerExportDataSetDetails` endpoint that accepts a chart context (chart ID or dataset group ID with view configuration), resolves the underlying dataset query, executes it to retrieve the full result set, and returns the data for export.

#### Scenario: Export data for a chart's underlying dataset
- **WHEN** a POST request is sent to `/datasetData/innerExportDataSetDetails` with a valid chart context identifier
- **THEN** the system resolves the chart's dataset, executes the base query without pagination limits, and returns the complete result set suitable for export

#### Scenario: Export for a chart that does not exist
- **WHEN** a POST request is sent to `/datasetData/innerExportDataSetDetails` with an invalid chart context identifier
- **THEN** the system returns an HTTP 404 error

### Requirement: Authentication and authorization for dataset data endpoints
All dataset data endpoints SHALL require a valid `X-DE-TOKEN` authentication header. Dataset data read operations SHALL require `use` permission on the `dataset` resource.

#### Scenario: Unauthenticated request to preview data
- **WHEN** a POST request is sent to `/datasetData/previewData` without a valid `X-DE-TOKEN` header
- **THEN** the system returns an HTTP 401 error

#### Scenario: Authenticated request to preview data
- **WHEN** a POST request is sent to `/datasetData/previewData` with a valid `X-DE-TOKEN` header and the user has dataset use permission
- **THEN** the system processes the request and returns the data
