## ADDED Requirements

### Requirement: The system SHALL expose a stable authentication status interface
The `/setting/authentication/status` endpoint SHALL evolve from an empty-array stub to a stable interface that describes available authentication methods, provider enable/disable states, and the default login selection.

#### Scenario: Authentication status returns provider list
- **WHEN** a client calls `GET /setting/authentication/status`
- **THEN** the system SHALL return a non-empty response describing all configured providers with their enable/disable states and the default login method

#### Scenario: Authentication status reflects provider changes
- **WHEN** an admin enables or disables a provider
- **THEN** the authentication status endpoint SHALL reflect the updated state on subsequent calls

#### Scenario: Default login method is indicated
- **WHEN** the authentication status is queried
- **THEN** the response SHALL indicate which login method is configured as default

### Requirement: The system SHALL allow admin configuration of default login method
Admins SHALL be able to configure the default login method (local login or a specific external provider) and modify it without disrupting active sessions.

#### Scenario: Admin sets local login as default
- **WHEN** an authenticated admin configures local login as the default method
- **THEN** the system SHALL persist this configuration and present local login as the primary login option

#### Scenario: Admin switches default to external provider
- **WHEN** an authenticated admin configures an enabled external provider as the default method
- **THEN** the system SHALL persist this configuration and present the external provider as the primary login option

#### Scenario: Non-admin cannot change default login
- **WHEN** a non-admin user attempts to change the default login method
- **THEN** the system SHALL reject the request with an authorization error

### Requirement: The system SHALL preserve local login as a safe fallback
Local login SHALL always remain functional regardless of external provider configuration. Disabling or failing external providers SHALL NOT break local login, share access, or embed access.

#### Scenario: Local login works when all providers disabled
- **WHEN** all external providers are disabled
- **THEN** local login SHALL continue to function normally, including `/login/localLogin` and `/login/refresh`

#### Scenario: Provider failure falls back to local login
- **WHEN** an external provider becomes unreachable during authentication
- **THEN** the system SHALL gracefully fall back to local login without affecting active sessions or share/embed paths

#### Scenario: Share and embed access unaffected by provider changes
- **WHEN** a provider is enabled, disabled, or reconfigured
- **THEN** existing share links and embedded resources SHALL continue to function using their existing token paths

### Requirement: The system SHALL manage provider lifecycle with enable/disable controls
Each identity provider SHALL have a lifecycle managed by admin actions: register, configure, enable, disable, and de-register. Disabled providers SHALL NOT appear as available login options.

#### Scenario: Admin enables a registered provider
- **WHEN** an authenticated admin enables a previously registered and configured provider
- **THEN** the system SHALL expose the provider as an available login option in the authentication status

#### Scenario: Admin disables an active provider
- **WHEN** an authenticated admin disables an active provider
- **THEN** the system SHALL remove the provider from available login options without breaking existing sessions or share/embed access

#### Scenario: Unregistered provider is not available
- **WHEN** a provider has not been registered in the system
- **THEN** it SHALL NOT appear in the authentication status or as a login option
