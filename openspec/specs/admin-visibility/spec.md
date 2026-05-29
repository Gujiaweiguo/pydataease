## ADDED Requirements

### Requirement: Admin console menu seeds SHALL cover org/user/role/permission entries
The `core_menu` table SHALL contain menu nodes for system settings, organization management, user management, role management, and permission management with proper parent-child hierarchy.

#### Scenario: Admin queries menu tree after migration
- **WHEN** an admin user calls `/menu/query` after migration
- **THEN** the response SHALL include menu entries for system, org, user, role, and permission management
- **AND** each entry SHALL have a valid `component` path matching an existing Vue page

### Requirement: Admin console permission points SHALL cover all admin menu entries
The `core_permission_point` table SHALL contain permission points for each admin console menu entry to enable role-based menu filtering.

#### Scenario: Permission points exist for admin menus
- **WHEN** the database is queried for permission points linked to admin menu IDs
- **THEN** each admin menu entry SHALL have at least a "view" permission point

### Requirement: TITLE_MAP SHALL cover all admin console menu entries
The `TITLE_MAP` in `menu_service.py` SHALL map every admin console menu name to a display title.

#### Scenario: Admin console menu items display titles
- **WHEN** `/menu/query` returns admin console entries
- **THEN** no entry SHALL have an empty or null title

### Requirement: Frontend SHALL have minimal page components for admin console entries
Each admin console menu entry's `component` path SHALL resolve to an existing Vue component in `src/views/system/`.

#### Scenario: Admin navigates to organization page
- **WHEN** admin clicks the organization menu item
- **THEN** a Vue page SHALL render with at least a title and placeholder container
- **AND** no dynamic import error SHALL appear in the browser console
