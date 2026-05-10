## ADDED Requirements

### Requirement: RSA public key discovery SHALL support the existing login client
The FastAPI backend SHALL expose a `GET /de2api/dekey` endpoint that returns the RSA public key material required by the frontend before credential submission.

#### Scenario: Login page requests the public key
- **WHEN** the frontend calls `GET /de2api/dekey`
- **THEN** the backend SHALL return a successful wrapped response containing the current RSA public key in the format expected by the existing client encryption logic

### Requirement: Local login SHALL accept RSA-encrypted credentials and issue frontend-compatible tokens
The FastAPI backend SHALL expose `POST /de2api/login/localLogin` that decrypts RSA-encrypted `name` and `pwd` fields, verifies the community user, and returns login data compatible with the current frontend flow.

#### Scenario: Community admin logs in successfully
- **WHEN** the client submits valid RSA-encrypted credentials for an enabled community user to `POST /de2api/login/localLogin`
- **THEN** the backend SHALL return a wrapped success response whose data includes a JWT token string and expiration metadata the frontend can persist for subsequent requests

#### Scenario: Login credentials are invalid
- **WHEN** the client submits an unknown account, bad password, or undecryptable credential payload to `POST /de2api/login/localLogin`
- **THEN** the backend SHALL reject the request with a compatible authentication failure response and SHALL NOT issue a token

#### Scenario: LDAP-style origin flag is present for community login
- **WHEN** the client includes `origin=1` in an otherwise valid local login request
- **THEN** the backend SHALL either handle the supported origin contract explicitly or return a controlled unsupported-auth response without crashing the login flow

### Requirement: Token refresh SHALL preserve the frontend session contract
The FastAPI backend SHALL expose `GET /de2api/login/refresh` that accepts the current `X-DE-TOKEN` header and `time` query parameter, validates the current user context, and returns a replacement token payload.

#### Scenario: Active session refreshes before expiry
- **WHEN** the client calls `GET /de2api/login/refresh?time=<timestamp>` with a valid current `X-DE-TOKEN`
- **THEN** the backend SHALL return a wrapped success response with a newly issued token and updated expiration data for the same authenticated user

#### Scenario: Invalid refresh token is supplied
- **WHEN** the client calls the refresh endpoint with a missing, invalid, or expired `X-DE-TOKEN`
- **THEN** the backend SHALL return a compatible authentication failure response and SHALL NOT mint a replacement token

### Requirement: Logout SHALL remain callable by the existing client
The FastAPI backend SHALL expose `GET /de2api/logout` so the frontend can complete its logout flow even when server-side community logout is a no-op.

#### Scenario: Authenticated user logs out
- **WHEN** the client calls `GET /de2api/logout` with its current token
- **THEN** the backend SHALL return a wrapped success response that allows the frontend to clear local auth state and redirect
