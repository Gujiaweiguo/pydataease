## ADDED Requirements

### Requirement: Row permissions SHALL filter dataset rows at query time
When a user queries a dataset, the system SHALL apply row-permission rules as WHERE clause filters, ensuring the user only sees rows they are authorized to access.

#### Scenario: User with row filter queries dataset
- **WHEN** a user with a row-permission rule `region = 'east'` queries a dataset
- **THEN** only rows where `region = 'east'` SHALL be returned

#### Scenario: Multiple row rules from different sources
- **WHEN** a user has row rules from both their org and their role
- **THEN** the rules SHALL be combined with AND logic (most restrictive)

### Requirement: Column permissions SHALL control field visibility
Column permissions SHALL support three actions: disable (field name and data hidden), desensitize (field name visible, data masked), and mask (partial data visible).

#### Scenario: Column with disable action
- **WHEN** a column has a disable rule for the current user
- **THEN** the column SHALL NOT appear in the query results

#### Scenario: Column with desensitize action
- **WHEN** a column has a desensitize rule for the current user
- **THEN** the column SHALL appear but values SHALL be masked (e.g., `138****5678`)

### Requirement: Column permission priority SHALL be user > role > org
When conflicting column-permission rules exist, user-level rules SHALL override role-level, which SHALL override org-level.

#### Scenario: User has direct grant overriding role rule
- **WHEN** a user's role disables column X but the user has a direct grant to view column X
- **THEN** column X SHALL be visible to the user

### Requirement: Whitelist SHALL exempt users from row/column rules
Users on the whitelist SHALL bypass row and column permission rules for the specified dataset.

#### Scenario: Whitelisted user queries restricted dataset
- **WHEN** a whitelisted user queries a dataset with row/column restrictions
- **THEN** the user SHALL see all rows and all columns without filtering or masking
