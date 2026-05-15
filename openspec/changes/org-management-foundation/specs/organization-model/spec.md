## ADDED Requirements

### Requirement: Organization tree SHALL support multi-level hierarchy with CRUD
The system SHALL manage organizations as a tree structure where each org may have a parent org and zero or more children.

#### Scenario: Admin creates a top-level organization
- **WHEN** an admin creates an org without specifying a parent
- **THEN** the org SHALL be created as a top-level node in the tree

#### Scenario: Admin creates a child organization
- **WHEN** an admin creates an org under an existing parent org
- **THEN** the new org SHALL appear as a child of the parent in the tree

#### Scenario: Admin deletes an organization with no children
- **WHEN** an admin deletes an org that has no child organizations
- **THEN** the org SHALL be removed and its user memberships SHALL be cleaned up

#### Scenario: Admin attempts to delete an organization with children
- **WHEN** an admin attempts to delete an org that still has child organizations
- **THEN** the system SHALL reject the deletion with a clear error

### Requirement: Users SHALL have organization membership
Each user SHALL belong to at least one organization; membership determines which orgs the user can switch into.

#### Scenario: User belongs to their default org after creation
- **WHEN** a user is created under an organization
- **THEN** the user SHALL have membership in that organization

#### Scenario: User attempts to switch to an org they do not belong to
- **WHEN** a user attempts to switch to an org where they have no membership
- **THEN** the system SHALL reject the switch with an authorization error

### Requirement: System admin SHALL bypass org membership restrictions
The built-in admin user SHALL be able to operate in any organization context regardless of explicit membership.

#### Scenario: Admin switches to any org
- **WHEN** the system admin switches to any organization
- **THEN** the switch SHALL succeed even without explicit membership

### Requirement: Current-org context SHALL be resolved and validated on every request
After login, the system SHALL know which org the user is operating in and SHALL validate that context is still valid.

#### Scenario: User token references an org the user was removed from
- **WHEN** a user's token contains an `oid` for an org the user no longer belongs to
- **THEN** the system SHALL reject the request and prompt re-authentication or org switch

## MODIFIED Requirements

### Requirement: Default root organization SHALL be seeded on first migration
The bootstrap migration SHALL create a default root organization and bind the admin user to it.

#### Scenario: Fresh database bootstrap
- **WHEN** the database is bootstrapped from scratch
- **THEN** a default root organization SHALL exist and the admin user SHALL be a member of it
