## ADDED Requirements

### Requirement: PostgreSQL SHALL be the primary persisted data platform
The migrated backend SHALL use PostgreSQL as the primary database platform for first-delivery runtime paths, replacing the Java backend’s MySQL/H2 primary path.

#### Scenario: First-delivery backend boots from an empty environment
- **WHEN** the new backend is started in a clean environment
- **THEN** it SHALL connect to PostgreSQL as its primary persisted store

### Requirement: Schema evolution SHALL be managed through Alembic
The migrated backend SHALL manage schema initialization and evolution through Alembic migrations and SHALL NOT rely on manually maintained production schemas outside the migration chain.

#### Scenario: New environment initialization
- **WHEN** a new environment is provisioned for the migrated backend
- **THEN** the PostgreSQL schema SHALL be creatable through Alembic upgrade execution to the current head revision

### Requirement: Data model migration SHALL account for platform differences
The migrated schema and persistence layer SHALL explicitly account for MySQL/H2 to PostgreSQL differences including auto-increment behavior, unsigned types, JSON fields, timestamps, booleans, and index or uniqueness semantics.

#### Scenario: Legacy schema concept is incompatible with PostgreSQL defaults
- **WHEN** a legacy table or field relies on a MySQL/H2-specific behavior
- **THEN** the migration design SHALL provide an explicit PostgreSQL-compatible mapping before the corresponding capability is released

### Requirement: Historical data migration SHALL be verifiable and reversible
The migration process SHALL verify representative historical data imports into PostgreSQL and SHALL define rollback via snapshots or equivalent recovery artifacts.

#### Scenario: Representative legacy data is migrated
- **WHEN** a representative data sample is imported into PostgreSQL during rehearsal
- **THEN** the import SHALL complete with constraint validation and SHALL have a documented rollback mechanism
