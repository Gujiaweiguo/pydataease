## Purpose
Ensures the Python FastAPI backend maintains contract compatibility with the shared Vue frontend by verifying route mounting, authentication behavior, response wrapping, and endpoint parity.

## Requirements

### Requirement: Contract tests SHALL use real AsyncClient against the ASGI app
Contract tests SHALL use `httpx.AsyncClient` with `ASGITransport` pointing at the FastAPI app instance, exercising the full middleware stack including auth, response wrapping, and routing.

##### Scenario: Contract test hits a protected endpoint
- **WHEN** a test sends a request without the `X-DE-TOKEN` header to an authenticated endpoint
- **THEN** the response SHALL have status 401

##### Scenario: Contract test hits an endpoint with valid auth
- **WHEN** a test sends a request with a valid JWT in `X-DE-TOKEN`
- **THEN** the response SHALL have status 200 and the body SHALL be wrapped in `ResultMessage` (`{"code": 0, "data": ..., "msg": ""}`)

### Requirement: Auth failure coverage SHALL be comprehensive
Contract tests SHALL verify that all authenticated endpoints return 401 for both missing tokens and invalid tokens.

##### Scenario: Missing token
- **WHEN** a request is made without `X-DE-TOKEN` header
- **THEN** the response SHALL be 401

##### Scenario: Invalid token
- **WHEN** a request is made with an invalid JWT string in `X-DE-TOKEN`
- **THEN** the response SHALL be 401

### Requirement: Unimplemented endpoints SHALL be explicitly skipped
Contract tests for endpoints not yet implemented in the Python backend SHALL be marked with `pytest.mark.skip` with a descriptive reason, not silently removed.

##### Scenario: Test suite runs against partially implemented backend
- **WHEN** the test suite executes
- **THEN** 42 contract tests SHALL pass and 17 SHALL be skipped (not fail) for unimplemented endpoints

### Requirement: Authorization management contract tests SHALL cover migrated auth APIs
Contract tests SHALL include the newly migrated authorization management endpoints and SHALL verify route mounting, authentication behavior, response wrapping, and at least one save-read permission flow.

##### Scenario: Auth management endpoints are not skipped
- **WHEN** the backend contract test suite runs after this change is implemented
- **THEN** tests for `/de2api/auth/busiResource/{flag}`, `/de2api/auth/menuResource`, `/de2api/auth/busiPermission`, `/de2api/auth/menuPermission`, `/de2api/auth/saveBusiPer`, `/de2api/auth/saveMenuPer`, `/de2api/auth/busiTargetPermission`, `/de2api/auth/menuTargetPermission`, `/de2api/auth/saveBusiTargetPer`, `/de2api/auth/saveMenuTargetPer`, and `/de2api/user/org/option` SHALL execute as implemented endpoint tests rather than being marked skipped as unimplemented

##### Scenario: Auth management endpoint returns wrapped success
- **WHEN** a contract test calls a supported auth management endpoint with a valid `X-DE-TOKEN`
- **THEN** the response SHALL use the backend `ResultMessage` wrapper with `code`, `data`, and `msg`

##### Scenario: Auth management endpoint rejects missing token
- **WHEN** a contract test calls a protected auth management endpoint without `X-DE-TOKEN`
- **THEN** the response SHALL be an authentication failure and SHALL NOT expose unwrapped internal errors
