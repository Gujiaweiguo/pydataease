## ADDED Requirements

### Requirement: Current user info retrieval
The backend SHALL provide a `GET /user/info` endpoint that returns the full profile of the currently authenticated user, including id, account, name, email, phone, enabled status, language, current organization id, and role assignments.

#### Scenario: Authenticated user requests own info
- **WHEN** an authenticated user sends `GET /user/info`
- **THEN** the backend SHALL return a user detail object with `id`, `account`, `name`, `email`, `phone`, `enable`, `language`, `oid`, and `roles` fields matching the authenticated user's record

#### Scenario: Unauthenticated request is rejected
- **WHEN** a request without a valid `X-DE-TOKEN` header sends `GET /user/info`
- **THEN** the backend SHALL return a 401 authentication error

### Requirement: Personal profile info retrieval
The backend SHALL provide a `GET /user/personInfo` endpoint that returns the personal profile of the currently authenticated user for the account settings page.

#### Scenario: Authenticated user requests personal info
- **WHEN** an authenticated user sends `GET /user/personInfo`
- **THEN** the backend SHALL return a user detail object with `id`, `account`, `name`, `email`, `phone`, `language`, and `oid` fields

### Requirement: Personal profile editing
The backend SHALL provide a `POST /user/personEdit` endpoint that allows the currently authenticated user to edit their own `name`, `email`, and `phone` fields. The endpoint SHALL NOT allow changing `account`, `oid`, `role_ids`, or `enable` status.

#### Scenario: User edits their own name
- **WHEN** an authenticated user sends `POST /user/personEdit` with `{"name": "New Name"}`
- **THEN** the backend SHALL update the user's `name` field and return the updated user detail

#### Scenario: User edits email and phone together
- **WHEN** an authenticated user sends `POST /user/personEdit` with `{"email": "new@test.com", "phone": "1234567890"}`
- **THEN** the backend SHALL update both fields and return the updated user detail

#### Scenario: Attempt to edit restricted fields is ignored
- **WHEN** an authenticated user sends `POST /user/personEdit` with `account` or `enable` fields
- **THEN** the backend SHALL ignore those fields and only update `name`, `email`, `phone`

### Requirement: Organization context switching
The backend SHALL provide a `POST /user/switch/{id}` endpoint that switches the authenticated user's current organization context. The backend SHALL verify the user belongs to the target organization before switching.

#### Scenario: User switches to an organization they belong to
- **WHEN** an authenticated user sends `POST /user/switch/{org_id}` where `org_id` is an organization they belong to
- **THEN** the backend SHALL return a new authentication token with the updated `oid` set to `org_id`

#### Scenario: User attempts to switch to an organization they do not belong to
- **WHEN** an authenticated user sends `POST /user/switch/{org_id}` where `org_id` is not an organization they belong to
- **THEN** the backend SHALL return a 403 error indicating the user is not a member of that organization

### Requirement: IP information retrieval
The backend SHALL provide a `GET /user/ipInfo` endpoint that returns the client's IP address as seen by the server.

#### Scenario: User requests IP info
- **WHEN** an authenticated user sends `GET /user/ipInfo`
- **THEN** the backend SHALL return an object containing the client's IP address derived from the request (preferring `X-Forwarded-For` header when present, otherwise `request.client.host`)
