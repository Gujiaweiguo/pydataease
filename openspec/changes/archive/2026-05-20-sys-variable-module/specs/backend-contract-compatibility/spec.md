## ADDED Requirements

### Requirement: SysVariable routes SHALL be mounted with backend contract behavior
The FastAPI backend SHALL expose the migrated `sysVariable` endpoints under `/de2api` and SHALL preserve standard authentication and response-wrapping behavior.

#### Scenario: Protected sysVariable route rejects missing token
- **WHEN** a client calls a protected `sysVariable` endpoint without `X-DE-TOKEN`
- **THEN** the backend SHALL return 401 rather than an unwrapped internal error

#### Scenario: Protected sysVariable route returns wrapped success
- **WHEN** a client calls a supported `sysVariable` endpoint with valid authentication
- **THEN** the response SHALL use the standard `ResultMessage` wrapper with `code`, `data`, and `msg`

### Requirement: Missing sysParameter compatibility endpoints SHALL be exposed
The FastAPI backend SHALL expose the expected `sysParameter` compatibility endpoints for online map lookup, UI/default settings, share base, and default login configuration.

#### Scenario: Online map endpoints are available
- **WHEN** a client calls `GET /sysParameter/queryOnlineMap`, `GET /sysParameter/queryOnlineMap/{type}`, or `POST /sysParameter/saveOnlineMap`
- **THEN** the backend SHALL return a wrapped success response compatible with the shared frontend contract

#### Scenario: Bootstrap sysParameter endpoints are available
- **WHEN** a client calls `GET /sysParameter/shareBase`, `GET /sysParameter/ui`, `GET /sysParameter/defaultSettings`, or `GET /sysParameter/defaultLogin`
- **THEN** the backend SHALL return a wrapped success response rather than 404
