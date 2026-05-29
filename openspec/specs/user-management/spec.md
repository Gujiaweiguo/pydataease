## ADDED Requirements

### Requirement: User CRUD SHALL be org-scoped
All user management operations SHALL operate within the current organization context.

#### Scenario: Admin creates a user in current org
- **WHEN** an admin creates a user while operating in org X
- **THEN** the user SHALL be created with membership in org X and assigned the specified roles within org X

#### Scenario: Admin lists users in current org
- **WHEN** an admin requests the user list
- **THEN** only users with membership in the current org SHALL be returned

### Requirement: User account SHALL be immutable after creation
The account field SHALL NOT be editable after the user is created.

#### Scenario: Admin edits user but cannot change account
- **WHEN** an admin edits a user's profile
- **THEN** the account field SHALL NOT be modifiable

### Requirement: Disabled users SHALL NOT be able to log in
When a user is disabled, login SHALL be rejected even with valid credentials.

#### Scenario: Disabled user attempts login
- **WHEN** a disabled user submits valid credentials
- **THEN** the system SHALL reject the login with an appropriate error

### Requirement: Role CRUD SHALL distinguish built-in and custom roles
Built-in roles (system-admin, org-admin, normal-user) SHALL NOT be editable or deletable. Custom roles SHALL inherit from a built-in org role.

#### Scenario: Admin creates a custom role
- **WHEN** an admin creates a custom role inheriting from org-admin
- **THEN** the custom role SHALL have permissions that do not exceed the parent built-in role

#### Scenario: Admin attempts to delete a built-in role
- **WHEN** an admin attempts to delete a built-in role
- **THEN** the system SHALL reject the operation

### Requirement: Removing a user's last role across all orgs SHALL delete the user
If unmounting a user from a role results in the user having zero roles across all organizations, the user SHALL be removed from the system.

#### Scenario: User loses last role
- **WHEN** a user is unmounted from their only remaining role across all orgs
- **THEN** the user SHALL be deleted from the system

### Requirement: Password reset SHALL use system default password
Admins SHALL be able to reset a user's password to the system-configured default.

#### Scenario: Admin resets user password
- **WHEN** an admin resets a user's password
- **THEN** the user's password SHALL be set to the system default password and the user SHALL be required to change it on next login
