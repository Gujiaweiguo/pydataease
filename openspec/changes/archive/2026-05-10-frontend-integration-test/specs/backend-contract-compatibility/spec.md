## MODIFIED Requirements

### Requirement: Contract tests SHALL use real AsyncClient against the ASGI app
Contract tests SHALL use `httpx.AsyncClient` with `ASGITransport` pointing at the FastAPI app instance, exercising the full middleware stack including auth, response wrapping, and routing. Additionally, E2E tests SHALL verify the same contract through real HTTP via the Vite proxy.

#### Scenario: Contract test hits a protected endpoint
- **WHEN** a test sends a request without the `X-DE-TOKEN` header to an authenticated endpoint
- **THEN** the response SHALL have status 401

#### Scenario: Contract test hits an endpoint with valid auth
- **WHEN** a test sends a request with a valid JWT in `X-DE-TOKEN`
- **THEN** the response SHALL have status 200 and the body SHALL be wrapped in `ResultMessage` (`{"code": 0, "data": ..., "msg": ""}`)

#### Scenario: E2E test confirms proxy does not corrupt response format
- **WHEN** an E2E test calls an authenticated endpoint through the Vite proxy
- **THEN** the response SHALL have the same `ResultMessage` structure as direct ASGI calls

### Requirement: Unimplemented endpoints SHALL be explicitly skipped
Contract tests for endpoints not yet implemented in the Python backend SHALL be marked with `pytest.mark.skip` with a descriptive reason, not silently removed.

#### Scenario: Test suite runs against partially implemented backend
- **WHEN** the test suite executes
- **THEN** 42 contract tests SHALL pass and 17 SHALL be skipped (not fail) for unimplemented endpoints
