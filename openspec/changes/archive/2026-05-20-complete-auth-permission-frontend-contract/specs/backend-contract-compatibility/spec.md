## ADDED Requirements

### Requirement: Authorization management contract tests SHALL cover migrated auth APIs
Contract tests SHALL include the newly migrated authorization management endpoints and SHALL verify route mounting, authentication behavior, response wrapping, and at least one save-read permission flow.

#### Scenario: Auth management endpoints are not skipped
- **WHEN** the backend contract test suite runs after this change is implemented
- **THEN** tests for `/de2api/auth/busiResource/{flag}`, `/de2api/auth/menuResource`, `/de2api/auth/busiPermission`, `/de2api/auth/menuPermission`, `/de2api/auth/saveBusiPer`, `/de2api/auth/saveMenuPer`, `/de2api/auth/busiTargetPermission`, `/de2api/auth/menuTargetPermission`, `/de2api/auth/saveBusiTargetPer`, `/de2api/auth/saveMenuTargetPer`, and `/de2api/user/org/option` SHALL execute as implemented endpoint tests rather than being marked skipped as unimplemented

#### Scenario: Auth management endpoint returns wrapped success
- **WHEN** a contract test calls a supported auth management endpoint with a valid `X-DE-TOKEN`
- **THEN** the response SHALL use the backend `ResultMessage` wrapper with `code`, `data`, and `msg`

#### Scenario: Auth management endpoint rejects missing token
- **WHEN** a contract test calls a protected auth management endpoint without `X-DE-TOKEN`
- **THEN** the response SHALL be an authentication failure and SHALL NOT expose unwrapped internal errors
