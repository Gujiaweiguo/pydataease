## MODIFIED Requirements

### Requirement: Sysvar rule resolution with per-user values
DataPermissionService.collect_row_filters() MUST resolve "sysvar" target_type rules by substituting the resolved system variable value for the current user into the filter_sql. The resolution MUST prefer user-scoped values (user_id = current user) over global values (user_id IS NULL). If no value exists at any scope, the rule MUST evaluate to default deny (1=0).

#### Scenario: User with user-scoped variable value
- **WHEN** user with id=42 has sysvar rule "region = ${region}" and user-scoped value region='east' exists AND global value region='all' exists
- **THEN** filter_sql becomes "region = 'east'" (user-scoped wins)

#### Scenario: User with only global variable value
- **WHEN** user with id=42 has sysvar rule "region = ${region}" and no user-scoped value exists but global value region='all' exists
- **THEN** filter_sql becomes "region = 'all'"

#### Scenario: User with no variable value at any scope
- **WHEN** user has sysvar rule "region = ${region}" and no value exists for that variable
- **THEN** rule evaluates to default deny (1=0)

#### Scenario: Sysvar priority in filter chain
- **WHEN** user has both user-level row rule and sysvar row rule for the same dataset
- **THEN** user-level rules take precedence over sysvar rules: user > sysvar > role > org
