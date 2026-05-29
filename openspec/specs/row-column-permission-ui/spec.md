## ADDED Requirements

### Requirement: Row permission rule UI SHALL support CRUD per dataset
The row permission page SHALL allow creating, viewing, editing, and deleting row filter rules for each dataset.

#### Scenario: Admin creates a row permission rule
- **WHEN** admin creates a row filter rule for a dataset targeting a role with filter condition `region = 'east'`
- **THEN** the rule SHALL be saved via the backend API
- **AND** the rule list SHALL refresh to show the new rule

#### Scenario: Admin deletes a row permission rule
- **WHEN** admin deletes an existing row permission rule
- **THEN** the rule SHALL be removed from the backend
- **AND** the dataset query SHALL no longer apply that filter

### Requirement: Column permission rule UI SHALL support disable/desensitize/mask actions
The column permission page SHALL allow creating column rules with three action types.

#### Scenario: Admin creates a column disable rule
- **WHEN** admin creates a column permission rule with action "disable" for a field
- **THEN** the field SHALL NOT appear in query results for the target user/role

#### Scenario: Admin creates a column desensitize rule
- **WHEN** admin creates a column permission rule with action "desensitize" for a phone field
- **THEN** the field values SHALL be masked (e.g., `138****5678`) for the target user/role

### Requirement: Whitelist UI SHALL allow exempting users from rules
The whitelist section SHALL allow adding and removing users who bypass row/column restrictions.

#### Scenario: Admin adds user to whitelist
- **WHEN** admin adds a user to the dataset whitelist
- **THEN** the user SHALL see all rows and all columns without filtering

### Requirement: Permission enforcement SHALL be verified with actual queries
Row and column permission rules SHALL be verified to actually affect dataset query results, not just be stored correctly.

#### Scenario: Row filter reduces visible rows
- **WHEN** a user with row filter `region = 'east'` queries a dataset
- **THEN** only rows matching the filter SHALL be returned

#### Scenario: Column desensitize masks values
- **WHEN** a user with column desensitize rule queries a dataset
- **THEN** masked field values SHALL show masked format instead of real data
