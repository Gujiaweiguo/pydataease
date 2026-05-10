## Capability: backend-contract-compatibility (delta)

Delta spec for the `resolve-backend-deferrals` change. Extends the existing `backend-contract-compatibility` capability with real test execution.

### MODIFIED Requirements

#### Requirement: Contract tests SHALL use real AsyncClient against the ASGI app
Contract tests SHALL use `httpx.AsyncClient` with `ASGITransport` pointing at the FastAPI app instance, exercising the full middleware stack including auth, response wrapping, and routing.

##### Scenario: Contract test hits a protected endpoint
- **WHEN** a test sends a request without the `X-DE-TOKEN` header to an authenticated endpoint
- **THEN** the response SHALL have status 401

##### Scenario: Contract test hits an endpoint with valid auth
- **WHEN** a test sends a request with a valid JWT in `X-DE-TOKEN`
- **THEN** the response SHALL have status 200 and the body SHALL be wrapped in `ResultMessage` (`{"code": 0, "data": ..., "msg": ""}`)

#### Requirement: Auth failure coverage SHALL be comprehensive
Contract tests SHALL verify that all authenticated endpoints return 401 for both missing tokens and invalid tokens.

##### Scenario: Missing token
- **WHEN** a request is made without `X-DE-TOKEN` header
- **THEN** the response SHALL be 401

##### Scenario: Invalid token
- **WHEN** a request is made with an invalid JWT string in `X-DE-TOKEN`
- **THEN** the response SHALL be 401

#### Requirement: Unimplemented endpoints SHALL be explicitly skipped
Contract tests for endpoints not yet implemented in the Python backend SHALL be marked with `pytest.mark.skip` with a descriptive reason, not silently removed.

##### Scenario: Test suite runs against partially implemented backend
- **WHEN** the test suite executes
- **THEN** 42 contract tests SHALL pass and 17 SHALL be skipped (not fail) for unimplemented endpoints
