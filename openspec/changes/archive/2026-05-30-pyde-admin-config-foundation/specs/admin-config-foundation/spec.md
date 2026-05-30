## ADDED Requirements

### Requirement: Admin configurations SHALL persist across process restarts
All admin-facing settings currently stored in process-memory variables (`_online_maps`, `_system_params`, etc.) SHALL be migrated to persistent storage backed by `CoreSysSetting`, ensuring that configuration survives process restarts and deployment cycles.

#### Scenario: Online map setting survives server restart
- **WHEN** an admin saves an online map configuration via `/sysParameter/basic/save`
- **AND** the server process is restarted
- **THEN** the saved map configuration SHALL still be readable via the corresponding query endpoint

#### Scenario: Request timeout setting survives server restart
- **WHEN** an admin saves a request timeout value
- **AND** the server process is restarted
- **THEN** the timeout value SHALL persist and be returned by subsequent reads

#### Scenario: Default login method survives server restart
- **WHEN** an admin configures a default login method
- **AND** the server process is restarted
- **THEN** the configured default login method SHALL remain active

### Requirement: CoreSysSetting SHALL use a unified key namespace
All settings stored in `CoreSysSetting` SHALL follow a consistent key naming convention with documented prefixes, default values, and type classification so that downstream changes can rely on stable key patterns.

#### Scenario: Key namespace follows documented convention
- **WHEN** a new setting is persisted via the admin configuration backbone
- **THEN** the key SHALL use the documented namespace prefix corresponding to its domain (e.g., `basic.*`, `ui.*`, `engine.*`)

#### Scenario: Missing keys return documented defaults
- **WHEN** a configuration key has never been set
- **THEN** the system SHALL return the documented default value rather than an error or null

### Requirement: Feature flags SHALL support safe rollback per capability
Each capability domain SHALL have a dedicated feature flag that can be disabled independently, stopping the capability's surface without requiring rollback of shared token/header/response semantics.

#### Scenario: Disabling a feature flag hides the capability
- **WHEN** an admin disables the feature flag for a capability (e.g., watermark, appearance, data-filing)
- **THEN** that capability's admin endpoints return disabled state, runtime behavior reverts to default, and no data is deleted

#### Scenario: Feature flag rollback preserves configuration data
- **WHEN** a feature flag is turned off
- **THEN** all previously saved configuration SHALL remain in storage, ready for re-enablement

#### Scenario: Rollback does not affect shared auth semantics
- **WHEN** a capability flag is disabled
- **THEN** shared token headers (`X-DE-TOKEN`, `X-DE-LINK-TOKEN`, `X-EMBEDDED-TOKEN`) and auth middleware SHALL continue operating without modification

### Requirement: Admin endpoints SHALL enforce permission boundaries
Management-plane write endpoints SHALL require authenticated admin access. Public read endpoints SHALL be explicitly classified and documented.

#### Scenario: Unauthenticated write to admin endpoint is rejected
- **WHEN** a client sends a write request to `/sysParameter/basic/save` without a valid admin token
- **THEN** the backend SHALL return a 401 or 403 response

#### Scenario: Authenticated non-admin write is rejected
- **WHEN** a client with a valid but non-admin token attempts to modify system settings
- **THEN** the backend SHALL return a 403 response

#### Scenario: Public read endpoints remain accessible
- **WHEN** a client requests a documented public endpoint (e.g., `/sysParameter/ui`, `/sysParameter/defaultLogin`)
- **THEN** the backend SHALL return the response without requiring authentication

## MODIFIED Requirements

### Requirement: System parameter endpoints SHALL return stable wrapped responses
All `/sysParameter/*` endpoints SHALL consistently return the `{"code": 0, "data": ..., "msg": ""}` response wrapper with typed, documented payload shapes.

#### Scenario: sysParameter query returns wrapped response
- **WHEN** a client sends a valid request to any `/sysParameter/*` endpoint
- **THEN** the response SHALL conform to the `ResultMessage` wrapper format

#### Scenario: Engine endpoint returns wrapped response
- **WHEN** a client sends a valid request to `/engine/*`
- **THEN** the response SHALL conform to the `ResultMessage` wrapper format
