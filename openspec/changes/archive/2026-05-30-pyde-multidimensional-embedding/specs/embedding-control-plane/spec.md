## ADDED Requirements

### Requirement: The system SHALL provide a unified runtime context model for share, link, and embed access
All share, link, and embed access paths SHALL resolve through a single coherent runtime context that defines token header responsibility boundaries, parameter precedence, and error handling consistently.

#### Scenario: Share access resolves through unified context
- **WHEN** a client accesses a shared resource via a valid share link token
- **THEN** the system SHALL resolve the access through the unified runtime context, applying share expiry, ticket validation, and password checks as applicable, and return the resource content or a structured error

#### Scenario: Embed access resolves through unified context
- **WHEN** a client accesses an embedded resource via `X-EMBEDDED-TOKEN` with outer params
- **THEN** the system SHALL resolve the access through the unified runtime context, injecting outer params via the canonical parameter resolution contract, and return the resource content or a structured error

#### Scenario: Expired share returns structured error
- **WHEN** a client accesses a shared resource with an expired share token
- **THEN** the system SHALL return a structured error response indicating expiry, not a generic 500

#### Scenario: Invalid ticket returns structured error
- **WHEN** a client accesses a ticket-protected share with an invalid ticket
- **THEN** the system SHALL return a structured error response indicating ticket invalidity

#### Scenario: Iframe context not allowed returns structured error
- **WHEN** an embed access is attempted from a domain not in the allowed list
- **THEN** the system SHALL return a structured error response indicating domain restriction

### Requirement: The system SHALL provide a multidimensional embedding control plane for admin configuration
Admins SHALL be able to configure embedding behavior per resource type (Dashboard, Chart, DataV, Data Filing reserved), including resource-level embed switches, domain policies, password/ticket/expiry rules, and parameter injection settings.

#### Scenario: Admin configures embed switch for a resource type
- **WHEN** an authenticated admin sends a request to enable or disable embedding for a specific resource type (e.g., Dashboard)
- **THEN** the system SHALL persist the switch state and enforce it at runtime, blocking embed access when disabled

#### Scenario: Admin configures domain policy for embed access
- **WHEN** an authenticated admin sets allowed domains for embedded access
- **THEN** the system SHALL persist the domain list and reject embed requests from non-allowed domains at runtime

#### Scenario: Admin configures password/ticket/expiry for a shared embed
- **WHEN** an authenticated admin configures password protection, ticket requirements, or expiry for an embed share
- **THEN** the system SHALL persist the configuration and enforce these rules on every embed access

#### Scenario: Non-admin cannot modify embed control plane
- **WHEN** a non-admin user attempts to modify embed control plane settings
- **THEN** the system SHALL reject the request with an authorization error

### Requirement: The system SHALL enforce parameter injection through the canonical parameter resolution contract
Outer params, jump params, busiFlag, and resource type context SHALL be resolved through the same canonical parameter resolution chain established by Change 3, not through embed-specific parsing.

#### Scenario: Outer params injected via canonical contract
- **WHEN** an embed access includes outer params
- **THEN** the system SHALL resolve them through the canonical parameter resolution contract with proper precedence over defaults

#### Scenario: Jump params resolved via canonical contract
- **WHEN** an embed access triggers a link jump with parameters
- **THEN** the system SHALL resolve jump parameters through the canonical contract alongside other runtime parameters

### Requirement: The system SHALL NOT introduce a second authentication header or embed protocol
All embed and share authentication SHALL extend the existing `X-DE-TOKEN` / `X-DE-LINK-TOKEN` / `X-EMBEDDED-TOKEN` chain. No new token headers or separate embed authentication protocols are permitted.

#### Scenario: Embed access uses existing token chain only
- **WHEN** an embed access is authenticated
- **THEN** it SHALL use only the existing token header chain (`X-EMBEDDED-TOKEN` extending `X-DE-LINK-TOKEN` and `X-DE-TOKEN`), with no additional authentication headers

#### Scenario: Share fallback to local token when embed context absent
- **WHEN** a share link is accessed without an embed context
- **THEN** the system SHALL fall back to standard `X-DE-TOKEN` or `X-DE-LINK-TOKEN` authentication as appropriate
