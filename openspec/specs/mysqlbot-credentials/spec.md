## ADDED Requirements

### Requirement: MySQLBot API Key storage and retrieval

The system SHALL store the MySQLBot advanced assistant API Key in the `sys_setting` table under the key `sqlbot.apiKey`. The key SHALL be readable and writable through the existing `SysSettingService`.

#### Scenario: Save API Key

- **WHEN** an admin sends a POST request to `/de2api/sysParameter/sqlbot` with payload `{"apiKey": "my-secret-key-123", ...}`
- **THEN** the system SHALL persist the value under the `sqlbot.apiKey` setting key

#### Scenario: Read API Key

- **WHEN** the system receives a MySQLBot callback request with `X-API-Key` header
- **THEN** the system SHALL read the stored `sqlbot.apiKey` value from the database and compare it with the request header value (constant-time comparison)

#### Scenario: Default API Key is empty

- **WHEN** no `sqlbot.apiKey` has been configured
- **THEN** the system SHALL treat it as an empty string, causing all MySQLBot API requests to be rejected with 401

### Requirement: API Key verification as FastAPI dependency

The system SHALL provide a FastAPI dependency function `verify_mysqlbot_apikey` that validates the `X-API-Key` header against the stored `sqlbot.apiKey` setting. All MySQLBot callback endpoints SHALL use this dependency.

#### Scenario: Valid API Key passes verification

- **WHEN** a request includes `X-API-Key: my-secret-key-123` and the stored setting matches
- **THEN** the dependency SHALL return without error, allowing the route handler to execute

#### Scenario: Missing API Key header

- **WHEN** a request does not include an `X-API-Key` header
- **THEN** the dependency SHALL raise HTTPException with status 401 and message "Missing API Key"

#### Scenario: Incorrect API Key

- **WHEN** a request includes `X-API-Key: wrong-key` and the stored setting does not match
- **THEN** the dependency SHALL raise HTTPException with status 401 and message "Invalid API Key"

### Requirement: MySQLBot integration mode setting

The system SHALL support a `sqlbot.mode` setting with values `"basic"` (default) or `"advanced"`. This setting controls which integration mode is active and is configurable through the existing system settings UI.

#### Scenario: Default mode is basic

- **WHEN** no `sqlbot.mode` has been configured
- **THEN** the system SHALL default to `"basic"`, maintaining backward compatibility with existing basic assistant integrations

#### Scenario: Switch to advanced mode

- **WHEN** an admin configures `sqlbot.mode` to `"advanced"` via the settings UI
- **THEN** the system SHALL enable the MySQLBot callback API endpoints and update the frontend settings UI to show advanced configuration options
