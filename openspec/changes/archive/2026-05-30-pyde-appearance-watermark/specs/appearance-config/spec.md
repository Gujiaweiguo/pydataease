## ADDED Requirements

### Requirement: Appearance settings SHALL be fully configurable and persistent
The backend SHALL expose stable API endpoints for reading and writing all appearance configuration items (site name, theme color, navbar style, login page assets, footer, help link, demo tip, font), with every item persisted through `CoreSysSetting` and surviving process restarts.

#### Scenario: Admin saves site name
- **WHEN** an admin sends a write request to save the site name via the appearance configuration endpoint
- **THEN** the backend SHALL persist the value and return a wrapped success response

#### Scenario: Site name persists after restart
- **WHEN** an admin has saved a custom site name
- **AND** the server process is restarted
- **THEN** subsequent reads SHALL return the saved site name, not a hardcoded default

#### Scenario: Login page reads appearance configuration
- **WHEN** an unauthenticated client requests the login page appearance settings
- **THEN** the backend SHALL return the persisted appearance values (site name, login background, theme color) via the public read endpoint

#### Scenario: Theme color change applies across all viewing contexts
- **WHEN** an admin saves a new theme color
- **THEN** the theme color SHALL be returned by the read endpoint for normal pages, login pages, share pages, and embedded pages

#### Scenario: Default values returned for unset appearance items
- **WHEN** an appearance configuration item has never been set
- **THEN** the backend SHALL return the documented default value

### Requirement: Appearance feature flag SHALL support safe rollback
The appearance capability SHALL have a dedicated feature flag. Disabling it SHALL revert to default styling without deleting saved configuration.

#### Scenario: Disabling appearance flag reverts to defaults
- **WHEN** the appearance feature flag is disabled
- **THEN** all appearance endpoints SHALL return default values, and saved configuration SHALL remain in storage
