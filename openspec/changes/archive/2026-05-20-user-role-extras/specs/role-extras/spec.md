## ADDED Requirements

### Requirement: Pre-unmount information retrieval
The backend SHALL provide a `POST /role/beforeUnmountInfo` endpoint that returns information about users before they are unmounted from a role. This allows the frontend to show a confirmation dialog with relevant details.

#### Scenario: Admin requests pre-unmount info for users
- **WHEN** an authenticated admin sends `POST /role/beforeUnmountInfo` with `{"roleId": rid, "userIds": [uid1, uid2]}`
- **THEN** the backend SHALL return a list of user details including `id`, `name`, `account`, and the number of remaining roles each user has in the current organization

#### Scenario: Non-existent role ID
- **WHEN** an authenticated admin sends `POST /role/beforeUnmountInfo` with a role ID that does not exist
- **THEN** the backend SHALL return a 404 error indicating the role was not found

#### Scenario: Non-existent user IDs are skipped
- **WHEN** an authenticated admin sends `POST /role/beforeUnmountInfo` with some user IDs that do not exist
- **THEN** the backend SHALL return info only for users that exist and are found, skipping missing ones without error

### Requirement: External user mounting to role
The backend SHALL provide a `POST /role/mountExternalUser` endpoint that mounts external users to a role by their account identifier (as opposed to internal user ID). The backend SHALL look up users by account and origin, then apply the same mounting logic as the existing `mountUser` endpoint.

#### Scenario: Admin mounts external user to role by account
- **WHEN** an authenticated admin sends `POST /role/mountExternalUser` with `{"roleId": rid, "accounts": ["extuser1", "extuser2"]}`
- **THEN** the backend SHALL look up each user by account, verify they are external-origin users, and mount them to the specified role

#### Scenario: External user account not found
- **WHEN** an authenticated admin sends `POST /role/mountExternalUser` with an account that does not exist
- **THEN** the backend SHALL skip that account and mount the remaining valid accounts. The response SHALL indicate which accounts were not found.

#### Scenario: Role does not exist
- **WHEN** an authenticated admin sends `POST /role/mountExternalUser` with a role ID that does not exist
- **THEN** the backend SHALL return a 404 error indicating the role was not found
