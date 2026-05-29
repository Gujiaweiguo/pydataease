## ADDED Requirements

### Requirement: Organization management page SHALL display org tree
The organization page SHALL call the existing org API and render the organization tree structure.

#### Scenario: Admin views organization tree
- **WHEN** admin navigates to the organization management page
- **THEN** the page SHALL load the org tree from the backend API
- **AND** display organizations in a tree structure

### Requirement: Organization CRUD SHALL be wired to existing backend APIs
Create, edit, and delete operations on the org page SHALL call existing backend org endpoints.

#### Scenario: Admin creates a top-level org
- **WHEN** admin creates a new organization from the management page
- **THEN** the backend org create API SHALL be called
- **AND** the tree SHALL refresh to show the new org

#### Scenario: Admin deletes a leaf org
- **WHEN** admin deletes an org with no children
- **THEN** the backend org delete API SHALL be called
- **AND** the org SHALL be removed from the tree
