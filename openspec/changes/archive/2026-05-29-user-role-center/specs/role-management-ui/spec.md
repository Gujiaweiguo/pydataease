## ADDED Requirements

### Requirement: Role management page SHALL list roles in current org
The role management page SHALL call the role query API filtered by current org context.

#### Scenario: Admin views role list
- **WHEN** admin navigates to role management
- **THEN** the page SHALL display roles belonging to the current org plus built-in system roles

### Requirement: Role CRUD SHALL use existing backend APIs
Create, edit, and delete operations SHALL call the corresponding `/role/*` endpoints.

#### Scenario: Admin creates a custom role
- **WHEN** admin creates a custom role inheriting from a built-in org role
- **THEN** the backend create API SHALL be called
- **AND** the role list SHALL refresh

#### Scenario: Admin attempts to delete built-in role
- **WHEN** admin tries to delete a built-in role
- **THEN** the UI SHALL show the backend error and NOT proceed with deletion

### Requirement: User-role binding UI SHALL support mount and unmount
The role detail page SHALL allow mounting users to roles and unmounting users from roles.

#### Scenario: Admin mounts user to role
- **WHEN** admin selects a user and mounts them to a role
- **THEN** the backend mount API SHALL be called
- **AND** the user SHALL appear in the role's member list

#### Scenario: Admin unmounts last role from user
- **WHEN** admin unmounts a user's last role across all orgs
- **THEN** the backend SHALL delete the user (as per backend logic)
- **AND** the user SHALL disappear from all user lists
