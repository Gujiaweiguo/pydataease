## ADDED Requirements

### Requirement: Existing frontend HTTP contracts SHALL remain compatible
The replacement FastAPI backend SHALL preserve the current frontend-facing HTTP contract baseline defined by `sdk/api/**/*Api.java` and `core/core-frontend/src/api/*.ts`, including route paths, request methods, and core response payload structures for first-delivery capabilities.

#### Scenario: Frontend requests a migrated endpoint
- **WHEN** the frontend calls a first-delivery backend endpoint that existed in the Java service
- **THEN** the FastAPI backend SHALL accept the same route path and HTTP method and SHALL return a compatible response structure

### Requirement: Contract characterization SHALL precede endpoint replacement
The migration process SHALL produce characterization tests and API inventory artifacts before replacing priority backend domains such as login, datasource, dataset, chart, visualization, share, export, and system settings.

#### Scenario: A domain is queued for migration
- **WHEN** a backend domain is selected for migration
- **THEN** a characterization test baseline and inventory entry for that domain SHALL already exist or be created first

### Requirement: Deferred or unsupported endpoints SHALL be explicitly declared
The FastAPI backend SHALL NOT silently omit first-delivery endpoints, and any deferred endpoint SHALL be explicitly declared and auditable.

#### Scenario: A requested endpoint is not implemented in first delivery
- **WHEN** a frontend or test attempts to use a deferred endpoint
- **THEN** the system SHALL expose it as an explicitly registered deferred capability rather than as an accidental missing route
