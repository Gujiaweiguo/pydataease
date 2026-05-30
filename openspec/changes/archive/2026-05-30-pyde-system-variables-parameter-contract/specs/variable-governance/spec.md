## ADDED Requirements

### Requirement: System variables SHALL follow governance rules for naming and typing
System variable definitions SHALL adhere to documented naming conventions, type classification, and dataset binding rules. Variables that don't meet these constraints SHALL be rejected at creation time.

#### Scenario: Variable name follows naming convention
- **WHEN** a user creates a system variable with a name that violates the naming convention
- **THEN** the backend SHALL reject the creation with a validation error

#### Scenario: Variable bound to dataset field resolves correctly
- **WHEN** a system variable is bound to a dataset field
- **THEN** the variable's selectable values SHALL be derived from that field's data, and the binding SHALL be validated at creation time

#### Scenario: Unbound variable allows manual value entry
- **WHEN** a system variable has no dataset field binding
- **THEN** administrators SHALL be able to manually create and manage selectable values

### Requirement: Variable CRUD SHALL be consistent with the parameter contract
All variable creation, editing, and deletion operations SHALL respect the canonical parameter resolution contract and permission boundaries.

#### Scenario: Variable creation validates against parameter contract
- **WHEN** a user creates a new system variable
- **THEN** the backend SHALL validate that the variable name, type, and binding conform to the parameter contract rules

#### Scenario: Variable deletion checks downstream dependencies
- **WHEN** a user deletes a system variable that is referenced by watermark templates or embedding configurations
- **THEN** the backend SHALL warn about or block the deletion if the variable is in active use

#### Scenario: Variable value changes propagate to dependent contexts
- **WHEN** a system variable's value is updated
- **THEN** subsequent parameter resolutions SHALL use the new value (watermark text, embedding params, etc.)

### Requirement: Variable resolution SHALL NOT bypass permission checks
System variable values SHALL only be resolved for contexts where the requesting user or session has appropriate access. Variable resolution SHALL NOT bypass dataset binding validation.

#### Scenario: Unauthorized variable access is rejected
- **WHEN** a user without variable read permission attempts to resolve a variable value
- **THEN** the backend SHALL return a permission error

#### Scenario: Dataset binding validation enforced at resolution time
- **WHEN** a variable is resolved in a context that requires dataset access
- **THEN** the backend SHALL verify that the requesting user has access to the bound dataset before returning the value

### Requirement: System variables SHALL NOT replace system parameter responsibilities
System variables SHALL serve runtime context, data filtering, and placeholder resolution. System parameters SHALL serve global configuration. The two domains SHALL share a resolution chain but not storage semantics.

#### Scenario: Variable does not serve as global configuration
- **WHEN** a client attempts to use a system variable as a substitute for a system parameter (e.g., setting a global timeout via variable)
- **THEN** the system SHALL not prevent this at the API level, but documentation and validation warnings SHALL clarify the boundary
