## ADDED Requirements

### Requirement: Backend APIs SHALL enforce resource-level authorization
All resource-access APIs (dashboard, screen, dataset, datasource) SHALL check user permissions before returning data or performing operations.

#### Scenario: User without view permission accesses dashboard
- **WHEN** a user without dashboard view permission requests a dashboard
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: User with manage permission edits resource
- **WHEN** a user with manage permission submits an edit to a resource
- **THEN** the edit SHALL succeed

### Requirement: Resource permission types SHALL include use, manage, authorize, view, export
The supported permission types for business resources SHALL be: use, manage, authorize, view, and export. Different resource types may support different subsets.

#### Scenario: Dataset supports use, manage, authorize
- **WHEN** permission catalog is queried for dataset resource type
- **THEN** supported permission types SHALL include use, manage, and authorize

#### Scenario: Dashboard supports view, export, manage, authorize
- **WHEN** permission catalog is queried for dashboard resource type
- **THEN** supported permission types SHALL include view, export, manage, and authorize
