## ADDED Requirements

### Requirement: Authentication headers SHALL remain compatible
The FastAPI backend SHALL support `X-DE-TOKEN`, `X-DE-LINK-TOKEN`, and `X-EMBEDDED-TOKEN` request header semantics for first-delivery flows that currently rely on those headers.

#### Scenario: Standard authenticated API request
- **WHEN** a client sends a valid `X-DE-TOKEN` to a protected endpoint
- **THEN** the backend SHALL authenticate the request and authorize it according to the migrated rules

### Requirement: Whitelist and protected route behavior SHALL remain compatible
The FastAPI backend SHALL preserve whitelist behavior for unauthenticated routes and SHALL return compatible failure behavior for missing, invalid, or expired tokens on protected routes.

#### Scenario: Whitelisted endpoint is accessed anonymously
- **WHEN** a client calls a whitelisted endpoint without an authentication token
- **THEN** the backend SHALL allow the request without requiring login

#### Scenario: Protected endpoint receives an invalid token
- **WHEN** a client calls a protected endpoint with a missing, invalid, or expired token
- **THEN** the backend SHALL return a compatible authentication or authorization error response without exposing internal stack traces

### Requirement: Shared-link and embedded flows SHALL be explicitly supported or rejected
The migrated backend SHALL either provide explicit compatibility for share-link and embedded authentication flows or explicitly reject unsupported flows before release.

#### Scenario: Share-link flow is in first-delivery scope
- **WHEN** a client presents a valid `X-DE-LINK-TOKEN` for a supported shared resource
- **THEN** the backend SHALL validate the token and enforce the corresponding access behavior

#### Scenario: Embedded or share flow is not supportable in current release
- **WHEN** release validation detects an unsupported embedded or shared-link flow in first-delivery scope
- **THEN** the release SHALL fail or the flow SHALL be formally marked out of scope before go-live

### Requirement: Response wrapping SHALL remain compatible for migrated routes
The FastAPI backend SHALL return a response wrapper and error structure that remains compatible with the frontend’s existing success and failure handling for migrated routes.

#### Scenario: Frontend handles a successful migrated request
- **WHEN** a migrated route returns a successful response
- **THEN** the returned JSON structure SHALL match the frontend’s expected wrapper semantics
