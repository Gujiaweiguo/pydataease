## ADDED Requirements

### Requirement: Sync datasource endpoints SHALL expose stubbed frontend-compatible responses
The system SHALL expose authenticated `/sync/datasource/**` endpoints for source pagination, target pagination, latest use lookup, validation, schema lookup, create, read, update, delete, batch delete, field listing, datasource listing by type, table listing, and validation by id. Each endpoint SHALL return the placeholder structure expected by the frontend until the real sync engine is implemented.

#### Scenario: Datasource list and lookup requests use empty placeholder payloads
- **WHEN** an authenticated client calls datasource pagination, latest use, schema lookup, field lookup, datasource list by type, or table list endpoints
- **THEN** the API returns HTTP 200 with empty list-style payloads or `{items: [], total: 0}` pagination payloads wrapped by the standard response envelope

#### Scenario: Datasource mutation and fetch requests remain callable before real backend logic exists
- **WHEN** an authenticated client calls datasource save, get by id, update, delete, or batch delete endpoints
- **THEN** the API returns HTTP 200 with empty object payloads wrapped by the standard response envelope instead of 404 or unimplemented errors

#### Scenario: Datasource validation stays explicitly negative in stub mode
- **WHEN** an authenticated client calls datasource validation by request body or by datasource id
- **THEN** the API returns HTTP 200 with a payload containing `valid: false` wrapped by the standard response envelope

### Requirement: Sync task endpoints SHALL expose stubbed task management responses
The system SHALL expose authenticated `/sync/task/**` endpoints for pagination, execution, start, stop, add, remove, batch delete, update, and get operations. These endpoints SHALL be callable by the frontend and SHALL return placeholder empty-object or empty-pagination payloads until the task scheduler integration exists.

#### Scenario: Task list requests return empty pagination data
- **WHEN** an authenticated client calls the sync task pagination endpoint
- **THEN** the API returns HTTP 200 with `{items: [], total: 0}` wrapped by the standard response envelope

#### Scenario: Task control and mutation requests remain available as stubs
- **WHEN** an authenticated client calls execute, start, stop, add, remove, batch delete, update, or get task endpoints
- **THEN** the API returns HTTP 200 with empty object payloads wrapped by the standard response envelope

### Requirement: Sync task log endpoints SHALL expose stubbed log responses
The system SHALL expose authenticated `/sync/task/log/**` endpoints for pagination, delete, detail, clear, and termination actions. These endpoints SHALL return placeholder payloads compatible with the frontend log views.

#### Scenario: Task log pagination returns an empty result set
- **WHEN** an authenticated client calls the task log pagination endpoint
- **THEN** the API returns HTTP 200 with `{items: [], total: 0}` wrapped by the standard response envelope

#### Scenario: Task log detail returns an empty completed stream
- **WHEN** an authenticated client calls the task log detail endpoint with a log id and starting line number
- **THEN** the API returns HTTP 200 with `{"logContent": "", "end": true}` wrapped by the standard response envelope

#### Scenario: Task log mutation actions remain callable before log execution exists
- **WHEN** an authenticated client calls task log delete, clear, or termination endpoints
- **THEN** the API returns HTTP 200 with empty object payloads wrapped by the standard response envelope

### Requirement: Sync summary endpoints SHALL expose stubbed dashboard summary data
The system SHALL expose authenticated `/sync/summary/**` endpoints for resource counts and log chart data so the frontend summary area can load without backend sync engine support.

#### Scenario: Resource count summary returns zero counts
- **WHEN** an authenticated client calls the sync summary resource count endpoint
- **THEN** the API returns HTTP 200 with `{"taskCount": 0, "sourceCount": 0}` wrapped by the standard response envelope

#### Scenario: Log chart summary returns an empty dataset
- **WHEN** an authenticated client calls the sync summary log chart data endpoint
- **THEN** the API returns HTTP 200 with an empty list wrapped by the standard response envelope

### Requirement: Sync stub endpoints SHALL remain protected by existing authentication
The system SHALL enforce the same token-based authentication on sync stub endpoints as other `/de2api` business routes.

#### Scenario: Unauthenticated sync requests are rejected
- **WHEN** a client calls a sync endpoint without a valid `X-DE-TOKEN`
- **THEN** the API returns HTTP 401 and does not expose the stub payload
