## ADDED Requirements

### Requirement: System variables SHALL support definition CRUD
The backend SHALL allow authenticated users to create, edit, inspect, delete, and query system variable definitions that include display metadata and optional dataset relationships.

#### Scenario: Authenticated user creates a variable definition
- **WHEN** a client sends `POST /sysVariable/create` with a valid `X-DE-TOKEN` and a valid variable payload
- **THEN** the backend SHALL persist the variable definition and return it through the standard wrapped success response

#### Scenario: Authenticated user edits a variable definition
- **WHEN** a client sends `POST /sysVariable/edit` for an existing variable definition
- **THEN** the backend SHALL update the stored fields and return the updated definition

#### Scenario: Authenticated user views variable detail
- **WHEN** a client sends `GET /sysVariable/detail/{id}` for an existing variable
- **THEN** the backend SHALL return the variable definition in the wrapped response

#### Scenario: Authenticated user deletes a variable definition
- **WHEN** a client sends `GET /sysVariable/delete/{id}` for an existing variable
- **THEN** the backend SHALL remove the variable definition and return a wrapped success response

#### Scenario: Authenticated user queries variable definitions
- **WHEN** a client sends `POST /sysVariable/query` with optional search filters
- **THEN** the backend SHALL return matching variable definitions in the wrapped response

### Requirement: System variables SHALL support value CRUD and selection paging
The backend SHALL allow authenticated users to manage selectable values for each variable definition, including list, page, create, edit, delete, and batch delete operations.

#### Scenario: Authenticated user pages variable values
- **WHEN** a client sends `POST /sysVariable/value/selected/{page}/{limit}` for a variable
- **THEN** the backend SHALL return a wrapped paginated result containing matching value rows and the total count

#### Scenario: Authenticated user lists all values for one variable
- **WHEN** a client sends `GET /sysVariable/value/selected/{id}`
- **THEN** the backend SHALL return the stored values for that variable in the wrapped response

#### Scenario: Authenticated user creates a variable value
- **WHEN** a client sends `POST /sysVariable/value/create` with a valid parent variable ID
- **THEN** the backend SHALL persist the value row and return the created entry

#### Scenario: Authenticated user edits a variable value
- **WHEN** a client sends `POST /sysVariable/value/edit` for an existing value row
- **THEN** the backend SHALL update the stored value fields and return the updated entry

#### Scenario: Authenticated user deletes one variable value
- **WHEN** a client sends `GET /sysVariable/value/delete/{id}` for an existing value row
- **THEN** the backend SHALL remove the row and return a wrapped success response

#### Scenario: Authenticated user batch deletes variable values
- **WHEN** a client sends `POST /sysVariable/value/batchDel` with multiple value IDs
- **THEN** the backend SHALL delete all matching value rows and return a wrapped success response
