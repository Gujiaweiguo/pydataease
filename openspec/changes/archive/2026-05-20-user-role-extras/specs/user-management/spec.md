## MODIFIED Requirements

### Requirement: Community users SHALL be persisted for authentication
The FastAPI backend SHALL persist authentication users in a `core_user` table with bigint identifiers, account identity fields, credential material, enabled state, organization context, language preference, origin, and audit timestamps. The `language` column SHALL be used to store and retrieve the user's display language preference across sessions.

#### Scenario: Default admin bootstrap exists after migration
- **WHEN** the authentication schema migration is applied to a new environment
- **THEN** the database SHALL contain an enabled `admin` community user record with the product's default bootstrap password stored using the backend's password utility

#### Scenario: Community user record is loaded for login
- **WHEN** the auth service looks up a user by login account
- **THEN** it SHALL receive the persisted `id`, `account`, `name`, `email`, `password_hash`, `enable`, `oid`, `language`, and `origin` values needed for verification and token issuance

#### Scenario: User language preference is persisted
- **WHEN** the user switches their display language via the switchLanguage endpoint
- **THEN** the updated language value SHALL be stored in the `core_user` record and reflected in subsequent token issuances
