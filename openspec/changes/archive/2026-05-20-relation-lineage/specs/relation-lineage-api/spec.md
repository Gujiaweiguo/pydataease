## ADDED Requirements

### Requirement: Datasource lineage endpoint SHALL list dependent dataset groups
The system SHALL expose an authenticated `POST /relation/datasource/{datasource_id}` endpoint that looks up dataset-table records by datasource and returns relation objects for each linked dataset group.

#### Scenario: Datasource has linked dataset groups
- **WHEN** an authenticated caller posts to `/relation/datasource/{datasource_id}` for a datasource referenced by dataset tables
- **THEN** the system SHALL return a list of objects containing the linked dataset group `id`, dataset table `name`, and relation `type` set to `dataset`

#### Scenario: Dataset table is missing a dataset group id
- **WHEN** a dataset-table record for the datasource has no `dataset_group_id`
- **THEN** the system SHALL omit that record from the lineage response

#### Scenario: Datasource lineage request is unauthenticated
- **WHEN** a caller posts to `/relation/datasource/{datasource_id}` without valid authentication
- **THEN** the system SHALL reject the request with an authentication failure status

### Requirement: Dataset lineage endpoint SHALL list dependent charts
The system SHALL expose an authenticated `POST /relation/dataset/{dataset_group_id}` endpoint that looks up chart views by dataset group and returns relation objects for the linked charts.

#### Scenario: Dataset group has linked charts
- **WHEN** an authenticated caller posts to `/relation/dataset/{dataset_group_id}` for a dataset group referenced by chart views
- **THEN** the system SHALL return a list of objects containing each chart `id`, chart `name`, relation `type` set to `chart`, and the owning visualization `sceneId`

#### Scenario: Dataset lineage request is unauthenticated
- **WHEN** a caller posts to `/relation/dataset/{dataset_group_id}` without valid authentication
- **THEN** the system SHALL reject the request with an authentication failure status

### Requirement: Visualization lineage endpoint SHALL list charts in the scene
The system SHALL expose an authenticated `POST /relation/dv/{dv_id}` endpoint that looks up chart views by visualization scene and returns relation objects for charts in that scene.

#### Scenario: Visualization has linked charts
- **WHEN** an authenticated caller posts to `/relation/dv/{dv_id}` for a visualization scene referenced by chart views
- **THEN** the system SHALL return a list of objects containing each chart `id`, chart `name`, relation `type` set to `chart`, and the linked dataset `tableId` when present

#### Scenario: Chart lacks linked dataset
- **WHEN** a chart in the visualization has no `table_id`
- **THEN** the system SHALL return `tableId` as `null` for that chart

#### Scenario: Visualization lineage request is unauthenticated
- **WHEN** a caller posts to `/relation/dv/{dv_id}` without valid authentication
- **THEN** the system SHALL reject the request with an authentication failure status
