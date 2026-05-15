## Capability: auth-runtime-compatibility (delta)

Delta spec for the `login-auth-flow` change. Extends the existing `auth-runtime-compatibility` capability with community login-runtime requirements.

## MODIFIED Requirements

### Requirement: Authentication headers SHALL remain compatible
The FastAPI backend SHALL support `X-DE-TOKEN`, `X-DE-LINK-TOKEN`, and `X-EMBEDDED-TOKEN` request header semantics for first-delivery flows that currently rely on those headers, and `X-DE-TOKEN` validation SHALL use the authenticated user's derived community signing secret rather than a single global JWT secret.

#### Scenario: Standard authenticated API request
- **WHEN** a client sends a valid `X-DE-TOKEN` to a protected endpoint
- **THEN** the backend SHALL authenticate the request by resolving the token's user context and verifying the signature with that user's derived signing secret before authorizing access

### Requirement: Whitelist and protected route behavior SHALL remain compatible
The FastAPI backend SHALL preserve whitelist behavior for unauthenticated routes and SHALL return compatible failure behavior for missing, invalid, disabled-user, or expired tokens on protected routes.

#### Scenario: Whitelisted endpoint is accessed anonymously
- **WHEN** a client calls a whitelisted endpoint without an authentication token
- **THEN** the backend SHALL allow the request without requiring login

#### Scenario: Protected endpoint receives an invalid token
- **WHEN** a client calls a protected endpoint with a missing, invalid, disabled-user, or expired token
- **THEN** the backend SHALL return a compatible authentication or authorization error response without exposing internal stack traces

### Requirement: Response wrapping SHALL remain compatible for migrated routes
The FastAPI backend SHALL return a response wrapper and error structure that remains compatible with the frontend’s existing success and failure handling for migrated routes, including login, refresh, and logout responses.

#### Scenario: Frontend handles a successful migrated request
- **WHEN** a migrated route returns a successful response
- **THEN** the returned JSON structure SHALL match the frontend’s expected wrapper semantics

#### Scenario: Frontend handles an authentication failure
- **WHEN** login, refresh, or protected-route authentication fails
- **THEN** the returned failure payload SHALL preserve the wrapper and error conventions the frontend uses to trigger retry, logout, or error messaging
