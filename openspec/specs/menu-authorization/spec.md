## ADDED Requirements

### Requirement: Menu tree SHALL be filtered by user effective permissions
The `/menu/query` endpoint SHALL return only menu items the user has permission to access, based on the union of org-level, role-level, and user-direct grants.

#### Scenario: User with limited role sees filtered menus
- **WHEN** a user with only "normal-user" role requests the menu tree
- **THEN** the response SHALL contain only menus permitted for normal-user, excluding admin-only items like system settings

#### Scenario: Admin sees all menus
- **WHEN** the system admin requests the menu tree
- **THEN** all menus SHALL be returned regardless of explicit permission grants

### Requirement: Effective permission SHALL be the union of org, role, and user grants
A user's effective permission for a given resource is the union (OR) of permissions granted at the organization level, role level, and directly to the user.

#### Scenario: User inherits org permission and has direct grant
- **WHEN** a user's org grants "view" for dashboards and the user also has a direct "manage" grant
- **THEN** the user SHALL have both "view" and "manage" permissions for dashboards
