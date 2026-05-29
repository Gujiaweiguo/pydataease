## ADDED Requirements

### Requirement: User management page SHALL provide paginated user list
The user management page SHALL call the user pagination API and display results in a table with search/filter within the current org context.

#### Scenario: Admin views user list
- **WHEN** admin navigates to user management
- **THEN** the page SHALL display a paginated table of users in the current organization

### Requirement: User CRUD operations SHALL call existing backend APIs
Create, edit, enable/disable, reset password, and batch delete operations SHALL call the corresponding `/user/*` endpoints.

#### Scenario: Admin creates a user
- **WHEN** admin fills in user creation form and submits
- **THEN** the backend create API SHALL be called with correct parameters
- **AND** the user list SHALL refresh to show the new user

#### Scenario: Admin resets user password
- **WHEN** admin clicks reset password for a user
- **THEN** the backend reset password API SHALL be called
- **AND** the user's password SHALL be set to the system default

### Requirement: Stub capabilities SHALL be explicitly marked
If batch import or other capabilities have backend stubs, the UI SHALL show a "not yet available" indicator rather than silently failing.

#### Scenario: User sees import button
- **WHEN** user views the user management page
- **THEN** any stub-import button SHALL be clearly marked as unavailable or hidden
