## ADDED Requirements

### Requirement: Dev environment SHALL start PostgreSQL, FastAPI, and Vue frontend together
The development environment SHALL provide a reproducible way to start all three services (PostgreSQL database, FastAPI backend on port 8100, Vue frontend on port 8080) so that the full stack is available for integration testing.

#### Scenario: All services start successfully
- **WHEN** the developer starts the dev environment
- **THEN** PostgreSQL SHALL be accessible on port 5432, FastAPI SHALL respond on port 8100, and the Vue frontend SHALL be accessible on port 8080

#### Scenario: Database migrations run before backend starts
- **WHEN** FastAPI starts
- **THEN** Alembic migrations SHALL have been applied and the database schema SHALL be current

#### Scenario: Default admin user is seeded
- **WHEN** the database is freshly migrated
- **THEN** a default admin user (username "admin", password "DataEase@123456") SHALL exist and be enabled

### Requirement: E2E test suite SHALL verify the login auth lifecycle through the browser
The system SHALL include a Playwright-based E2E test suite that drives the Vue frontend browser to verify the complete login authentication lifecycle against the FastAPI backend.

#### Scenario: User fetches RSA public key
- **WHEN** the E2E test navigates to the login page
- **THEN** the frontend SHALL call `GET /api/dekey` through the Vite proxy and receive a valid RSA public key

#### Scenario: User logs in with encrypted credentials
- **WHEN** the E2E test fills in username "admin" and password "DataEase@123456" and submits the login form
- **THEN** the frontend SHALL encrypt the password with the RSA public key, POST to `/api/login/localLogin`, and receive a JWT token in the response

#### Scenario: Authenticated user accesses protected endpoint
- **WHEN** the E2E test uses the JWT token from login to call a protected endpoint
- **THEN** the backend SHALL respond with status 200 and valid data wrapped in ResultMessage format

#### Scenario: User refreshes their token
- **WHEN** the E2E test calls `GET /api/login/refresh` with the current JWT
- **THEN** the backend SHALL return a new valid JWT token

#### Scenario: User logs out
- **WHEN** the E2E test calls `GET /api/logout` with the current JWT
- **THEN** the backend SHALL return a success response

### Requirement: API path routing SHALL correctly translate frontend requests to backend handlers
The Vite dev proxy SHALL correctly route frontend `/api/*` requests to the FastAPI backend's `/de2api/*` endpoints without path corruption or header loss.

#### Scenario: Login endpoint is reachable through proxy
- **WHEN** the frontend sends `POST /api/login/localLogin`
- **THEN** the request SHALL be proxied to `http://localhost:8100/de2api/login/localLogin` and receive a valid response

#### Scenario: Public key endpoint is reachable through proxy
- **WHEN** the frontend sends `GET /api/dekey`
- **THEN** the request SHALL be proxied to `http://localhost:8100/de2api/dekey` and receive the RSA public key

### Requirement: Response format SHALL match frontend expectations
The FastAPI backend's `ResultMessage` response wrapper SHALL produce JSON responses that the frontend axios interceptors can parse without modification.

#### Scenario: Successful response format
- **WHEN** the frontend receives a successful API response
- **THEN** the response body SHALL contain `{"code": 0, "data": <payload>, "msg": ""}` with camelCase field names in the data payload

#### Scenario: Error response format
- **WHEN** the frontend receives an error API response
- **THEN** the response body SHALL contain `{"code": <non-zero>, "data": null, "msg": "<error description>"}`
