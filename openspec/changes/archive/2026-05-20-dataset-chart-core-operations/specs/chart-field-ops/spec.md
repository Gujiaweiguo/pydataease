## ADDED Requirements

### Requirement: List chart fields by dimension and quota
The system SHALL provide a `POST /chart/listByDQ/{id}/{chartId}` endpoint that accepts a dataset group ID (`id`) and a chart ID (`chartId`) as path parameters, retrieves the dataset's fields filtered by the chart context, and returns them organized by group type (dimension fields and quota fields).

#### Scenario: List fields for a chart with both dimensions and quotas
- **WHEN** a POST request is sent to `/chart/listByDQ/{datasetGroupId}/{chartId}` with valid IDs
- **THEN** the system returns the dataset fields associated with the chart, categorized into dimension and quota groups

#### Scenario: List fields for a chart with only dimensions
- **WHEN** a POST request is sent to `/chart/listByDQ/{datasetGroupId}/{chartId}` for a chart that only has dimension fields
- **THEN** the system returns dimension fields and an empty quota fields list

#### Scenario: List fields for a non-existent dataset
- **WHEN** a POST request is sent to `/chart/listByDQ/{datasetGroupId}/{chartId}` with a dataset group ID that does not exist
- **THEN** the system returns an HTTP 404 error

### Requirement: Copy a field to a chart
The system SHALL provide a `POST /chart/copyField/{id}/{chartId}` endpoint that accepts a source field ID (`id`) and a target chart ID (`chartId`) as path parameters, creates a copy of the source field as a chart-specific custom field (with `chart_id` set to the target chart and `ext_field` set to indicate a custom field), and returns the new field.

#### Scenario: Copy a dimension field to a chart
- **WHEN** a POST request is sent to `/chart/copyField/{fieldId}/{chartId}` with a valid field ID and chart ID
- **THEN** the system creates a new `CoreDatasetTableField` record with the same field properties, sets `chart_id` to the target chart, sets `ext_field` to indicate a custom/copied field, generates a new ID, and returns the created field

#### Scenario: Copy a field to a non-existent chart
- **WHEN** a POST request is sent to `/chart/copyField/{fieldId}/{chartId}` with a chart ID that does not exist
- **THEN** the system returns an HTTP 404 error

#### Scenario: Copy a non-existent field
- **WHEN** a POST request is sent to `/chart/copyField/{fieldId}/{chartId}` with a field ID that does not exist
- **THEN** the system returns an HTTP 404 error

### Requirement: Delete a chart custom field
The system SHALL provide a `POST /chart/deleteField/{id}` endpoint that accepts a field ID as a path parameter, verifies the field is a chart custom field (has a non-zero `chart_id`), and deletes it from the database.

#### Scenario: Delete an existing chart custom field
- **WHEN** a POST request is sent to `/chart/deleteField/{fieldId}` with a valid chart custom field ID
- **THEN** the system deletes the field record and returns a success response

#### Scenario: Delete a non-existent field
- **WHEN** a POST request is sent to `/chart/deleteField/{fieldId}` with a field ID that does not exist
- **THEN** the system returns an HTTP 404 error

#### Scenario: Delete a dataset base field (not a chart custom field)
- **WHEN** a POST request is sent to `/chart/deleteField/{fieldId}` with a field ID that is a dataset-level field (chart_id is null/zero)
- **THEN** the system returns an HTTP 400 error indicating the field cannot be deleted through this endpoint

### Requirement: Delete all custom fields for a chart
The system SHALL provide a `POST /chart/deleteFieldByChart/{chartId}` endpoint that accepts a chart ID as a path parameter and deletes all custom fields (fields with `chart_id` matching the given chart ID) from the database.

#### Scenario: Delete all custom fields for a chart with custom fields
- **WHEN** a POST request is sent to `/chart/deleteFieldByChart/{chartId}` with a valid chart ID
- **THEN** the system deletes all field records where `chart_id` equals the given chart ID and returns a success response

#### Scenario: Delete all custom fields for a chart with no custom fields
- **WHEN** a POST request is sent to `/chart/deleteFieldByChart/{chartId}` for a chart with no custom fields
- **THEN** the system returns a success response (no-op)

### Requirement: Authentication for chart field endpoints
All chart field endpoints SHALL require a valid `X-DE-TOKEN` authentication header via the `get_current_user` dependency.

#### Scenario: Unauthenticated request to list chart fields
- **WHEN** a POST request is sent to `/chart/listByDQ/{id}/{chartId}` without a valid `X-DE-TOKEN` header
- **THEN** the system returns an HTTP 401 error
