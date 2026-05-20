## ADDED Requirements

### Requirement: Get field enumeration data for chart filter
The system SHALL provide a `POST /chartData/getFieldData/{fieldId}/{fieldType}` endpoint that accepts a field ID and field type as path parameters, and an optional request body with filter context (chart ID, dataset group ID). The system resolves the field's datasource and dataset, executes a `SELECT DISTINCT` query for that field with applied chart filters, and returns the enumeration data for use in chart filter dropdowns.

#### Scenario: Get enumeration data for a chart filter field
- **WHEN** a POST request is sent to `/chartData/getFieldData/{fieldId}/{fieldType}` with a valid field ID and field type
- **THEN** the system resolves the field's dataset, builds a distinct-values query considering any active chart filters, executes it, and returns the list of distinct values

#### Scenario: Get enumeration data for a non-existent field
- **WHEN** a POST request is sent to `/chartData/getFieldData/{fieldId}/{fieldType}` with a field ID that does not exist
- **THEN** the system returns an HTTP 404 error

#### Scenario: Get enumeration data with a filter applied
- **WHEN** a POST request is sent to `/chartData/getFieldData/{fieldId}/{fieldType}` with a filter context that restricts the base data
- **THEN** the system applies the filter to the base query before extracting distinct values, returning only values visible under the filter

### Requirement: Get drill-down field data
The system SHALL provide a `POST /chartData/getDrillFieldData/{fieldId}` endpoint that accepts a drill-down field ID as a path parameter and a request body containing the current drill context (chart ID, current dimension values, drill path). The system builds a query that filters by the current drill path context and returns the distinct values for the next drill-down level.

#### Scenario: Drill down to the next level
- **WHEN** a POST request is sent to `/chartData/getDrillFieldData/{fieldId}` with a valid drill field ID and a drill context containing current dimension values
- **THEN** the system builds a query filtered by the current drill path, extracts distinct values for the drill-down field, and returns them

#### Scenario: Drill down without prior context
- **WHEN** a POST request is sent to `/chartData/getDrillFieldData/{fieldId}` without any prior drill context (first drill level)
- **THEN** the system returns all distinct values for the drill field from the full dataset

#### Scenario: Drill down with a non-existent field
- **WHEN** a POST request is sent to `/chartData/getDrillFieldData/{fieldId}` with a field ID that does not exist
- **THEN** the system returns an HTTP 404 error

### Requirement: Check if two charts share the same dataset
The system SHALL provide a `GET /chart/checkSameDataSet/{viewIdSource}/{viewIdTarget}` endpoint that accepts two chart view IDs as path parameters, looks up the `table_id` (dataset group ID) for each chart, and returns a boolean indicating whether both charts reference the same dataset.

#### Scenario: Two charts sharing the same dataset
- **WHEN** a GET request is sent to `/chart/checkSameDataSet/{viewIdSource}/{viewIdTarget}` where both charts have the same `table_id`
- **THEN** the system returns `{data: true}` indicating the charts share the same dataset

#### Scenario: Two charts with different datasets
- **WHEN** a GET request is sent to `/chart/checkSameDataSet/{viewIdSource}/{viewIdTarget}` where the charts have different `table_id` values
- **THEN** the system returns `{data: false}` indicating the charts use different datasets

#### Scenario: Source chart does not exist
- **WHEN** a GET request is sent to `/chart/checkSameDataSet/{viewIdSource}/{viewIdTarget}` with a source view ID that does not exist
- **THEN** the system returns `{data: false}` (defensive: treat missing charts as not sharing)

#### Scenario: Target chart does not exist
- **WHEN** a GET request is sent to `/chart/checkSameDataSet/{viewIdSource}/{viewIdTarget}` with a target view ID that does not exist
- **THEN** the system returns `{data: false}` (defensive: treat missing charts as not sharing)

### Requirement: Authentication for chart data endpoints
All chart data enumeration endpoints SHALL require a valid `X-DE-TOKEN` authentication header via the `get_current_user` dependency.

#### Scenario: Unauthenticated request to get field data
- **WHEN** a POST request is sent to `/chartData/getFieldData/{fieldId}/{fieldType}` without a valid `X-DE-TOKEN` header
- **THEN** the system returns an HTTP 401 error
