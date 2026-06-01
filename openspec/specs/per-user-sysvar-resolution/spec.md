## ADDED Requirements

### Requirement: User-scoped variable value storage
The system SHALL allow variable values to be associated with a specific user via a nullable `user_id` column on `core_sys_variable_value`. Values with `user_id IS NULL` SHALL be treated as global values. Values with a specific `user_id` SHALL be treated as user-scoped.

#### Scenario: Create a user-scoped variable value
- **WHEN** admin creates a variable value with `userId` set to a valid user ID
- **THEN** the system stores the value with `user_id` set to that user ID

#### Scenario: Create a global variable value
- **WHEN** admin creates a variable value without `userId`
- **THEN** the system stores the value with `user_id` IS NULL

### Requirement: User-scoped resolution priority
The system SHALL resolve variable values with the following priority: user-scoped value (user_id = current user) > global value (user_id IS NULL) > default deny (1=0). If multiple user-scoped values exist for the same variable and user, the first by create_time ASC SHALL be used.

#### Scenario: User has user-scoped value
- **WHEN** user with id=42 resolves variable `store_name` and a user-scoped value exists (user_id=42, value="蓝墨店") and a global value exists (value="所有店铺")
- **THEN** the system returns "蓝墨店"

#### Scenario: User has no user-scoped value, global exists
- **WHEN** user with id=42 resolves variable `store_name` and no user-scoped value exists for user_id=42, but a global value exists (value="所有店铺")
- **THEN** the system returns "所有店铺"

#### Scenario: No value exists at all
- **WHEN** user resolves variable `store_name` and no value exists for any user_id
- **THEN** the system returns default deny (1=0 in filter SQL)

### Requirement: Person sysvar info endpoint
The system SHALL expose `GET /user/personSysVariableInfo/{uid}` returning all system variables with their resolved values for the specified user, using the same resolution priority.

#### Scenario: Query user's resolved variables
- **WHEN** admin requests `GET /user/personSysVariableInfo/42`
- **THEN** the system returns all variables with each variable's resolved value for user 42

### Requirement: Frontend user assignment for variable values
The frontend sysvar value management page SHALL allow selecting a user when creating or editing a variable value. The value list SHALL display the assigned user (if any) in a column.

#### Scenario: Admin assigns user during value creation
- **WHEN** admin opens the value create dialog and selects a user from the user selector
- **THEN** the created value is associated with that user

#### Scenario: Value list shows user column
- **WHEN** admin views the value list for a variable
- **THEN** each row shows the assigned user name (or "全局" for global values)
