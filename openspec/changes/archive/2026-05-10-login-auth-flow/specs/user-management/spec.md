## ADDED Requirements

### Requirement: Community users SHALL be persisted for authentication
The FastAPI backend SHALL persist authentication users in a `core_user` table with bigint identifiers, account identity fields, credential material, enabled state, organization context, origin, and audit timestamps.

#### Scenario: Default admin bootstrap exists after migration
- **WHEN** the authentication schema migration is applied to a new environment
- **THEN** the database SHALL contain an enabled `admin` community user record with the product's default bootstrap password stored using the backend's password utility

#### Scenario: Community user record is loaded for login
- **WHEN** the auth service looks up a user by login account
- **THEN** it SHALL receive the persisted `id`, `account`, `name`, `email`, `password_hash`, `enable`, `oid`, and `origin` values needed for verification and token issuance

### Requirement: Password operations SHALL separate storage from token-secret derivation
The backend SHALL store verifiable password hashes for login and SHALL provide a deterministic per-user secret derivation function for JWT compatibility without requiring plaintext password storage.

#### Scenario: Password verification succeeds for a valid login
- **WHEN** a login attempt supplies credentials matching the stored password hash
- **THEN** the password utility SHALL report the credential as valid without exposing the original password value

#### Scenario: JWT secret derivation is requested for a persisted user
- **WHEN** token issuance or token validation needs that user's signing secret
- **THEN** the password utility SHALL derive the same compatibility secret for that user from persisted credential material every time

### Requirement: Disabled community users SHALL be blocked from authentication
The backend SHALL reject login and token refresh for community users whose persisted record is disabled.

#### Scenario: Disabled user attempts login
- **WHEN** a disabled user submits otherwise valid credentials
- **THEN** the backend SHALL reject the login attempt with a compatible authentication failure response

#### Scenario: Disabled user attempts refresh
- **WHEN** a valid token belongs to a user whose record has been disabled since issuance
- **THEN** the refresh flow SHALL reject reissuance rather than minting a new token
