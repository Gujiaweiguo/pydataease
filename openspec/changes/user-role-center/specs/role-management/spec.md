## ADDED Requirements

### Requirement: Roles SHALL belong to an organization
Each role SHALL be scoped to a specific organization. Built-in system roles are global.

#### Scenario: List roles in current org
- **WHEN** a user requests roles for the current org
- **THEN** only roles belonging to that org plus built-in system roles SHALL be returned

### Requirement: Custom roles SHALL inherit from a built-in org role
Custom roles SHALL be created by inheriting from an existing built-in organization role and cannot exceed the parent's permission ceiling.

#### Scenario: Create custom role with valid parent
- **WHEN** an admin creates a custom role inheriting from the org-admin built-in role
- **THEN** the custom role SHALL be created and its permissions SHALL not exceed org-admin level

### Requirement: User-role binding SHALL be org-scoped
A user can hold multiple roles within an organization, and the same user can hold different roles in different organizations.

#### Scenario: User has different roles in different orgs
- **WHEN** a user has org-admin role in org A and normal-user role in org B
- **THEN** the user SHALL have org-admin permissions when operating in org A and normal-user permissions in org B

### Requirement: Role member management SHALL support mount and unmount
Roles SHALL support adding (mounting) and removing (unmounting) users.

#### Scenario: Mount existing org user to role
- **WHEN** an admin mounts an existing org user to a custom role
- **THEN** the user SHALL gain the role's permissions within that org

#### Scenario: Mount external user to role
- **WHEN** an admin searches for a user by account/ID and mounts them to a role in the current org
- **THEN** the user SHALL be granted membership in the org and the specified role
