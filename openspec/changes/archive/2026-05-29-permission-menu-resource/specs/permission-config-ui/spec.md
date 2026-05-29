## ADDED Requirements

### Requirement: Permission configuration page SHALL display menu tree with grant controls
The permission page SHALL show the full menu tree and allow admins to grant or revoke menu access per role or user.

#### Scenario: Admin grants menu permission to role
- **WHEN** admin selects a role and checks a menu item in the permission tree
- **AND** saves the configuration
- **THEN** the backend SHALL update the role's permission grants
- **AND** role members SHALL see the menu item on next `/menu/query` call

#### Scenario: Admin revokes menu permission from role
- **WHEN** admin unchecks a menu item for a role and saves
- **THEN** the backend SHALL remove the permission grant
- **AND** role members SHALL no longer see the menu item

### Requirement: Permission configuration page SHALL display resource tree with permission types
The resource permission section SHALL show dashboards, screens, datasets, and datasources with configurable permission types (use/manage/authorize/view/export).

#### Scenario: Admin grants resource permission
- **WHEN** admin selects a resource and assigns a permission type to a role
- **THEN** the backend SHALL store the grant
- **AND** the role member SHALL have the specified access level

### Requirement: Permission changes SHALL immediately affect `/menu/query` results
After saving permission configuration, the menu tree returned by `/menu/query` SHALL reflect the changes.

#### Scenario: Permission change reflected in menu query
- **WHEN** admin revokes a menu permission for a role
- **THEN** subsequent `/menu/query` calls by role members SHALL exclude the revoked menu

### Requirement: Org admin authorization boundary SHALL be enforced
Org admins SHALL only be able to manage permissions within their own organization.

#### Scenario: Org admin attempts cross-org permission change
- **WHEN** org A admin attempts to modify permissions for org B resources
- **THEN** the backend SHALL reject the request with 403
