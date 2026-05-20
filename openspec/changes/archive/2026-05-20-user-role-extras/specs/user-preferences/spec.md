## ADDED Requirements

### Requirement: Display language switching
The backend SHALL provide a `POST /user/switchLanguage` endpoint that updates the authenticated user's display language preference and returns a new authentication token reflecting the change.

#### Scenario: User switches language
- **WHEN** an authenticated user sends `POST /user/switchLanguage` with `{"language": "en"}`
- **THEN** the backend SHALL update the user's `language` field in the database and return a new authentication token with the updated `language` claim

#### Scenario: Invalid language value is accepted
- **WHEN** an authenticated user sends `POST /user/switchLanguage` with an unrecognized language code
- **THEN** the backend SHALL still update the language field and return a new token. Language validation is the frontend's responsibility.

### Requirement: User system variable info retrieval
The backend SHALL provide a `GET /user/personSysVariableInfo/{uid}` endpoint that returns system variable preferences for the specified user.

#### Scenario: User requests system variable info
- **WHEN** an authenticated user sends `GET /user/personSysVariableInfo/{uid}`
- **THEN** the backend SHALL return an empty object `{}` since the system variable module is not yet implemented. This is a placeholder endpoint to prevent frontend 404 errors.

#### Scenario: Unauthenticated request is rejected
- **WHEN** a request without a valid token sends `GET /user/personSysVariableInfo/{uid}`
- **THEN** the backend SHALL return a 401 authentication error
