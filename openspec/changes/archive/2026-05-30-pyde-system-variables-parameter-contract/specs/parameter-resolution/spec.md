## ADDED Requirements

### Requirement: Parameter resolution SHALL follow a single canonical contract
All parameter resolution across the system SHALL use one documented contract defining source priority, conflict resolution, null handling, required-field enforcement, and error feedback. No subsystem SHALL define its own independent priority rules.

#### Scenario: Higher-priority source overrides lower-priority source
- **WHEN** a parameter key exists in both embedding context and system variables
- **THEN** the value from embedding context (higher priority) SHALL be used

#### Scenario: Missing required parameter produces explicit error
- **WHEN** a required parameter resolves to null across all sources
- **THEN** the system SHALL return an error response indicating the missing parameter key and which sources were checked

#### Scenario: Optional parameter falls back to default value
- **WHEN** an optional parameter is not provided by any source
- **THEN** the system SHALL use the documented default value for that parameter

#### Scenario: Outer params override system variables
- **WHEN** a parameter exists in both outer params and system variables
- **THEN** the outer params value SHALL take precedence

#### Scenario: Template placeholder resolves to variable value
- **WHEN** a template contains a placeholder referencing a system variable
- **THEN** the placeholder SHALL be resolved using the variable's current value through the canonical resolution chain

### Requirement: Parameter resolution SHALL support five-stage processing
Every parameter SHALL be processed through source identification, parsing, normalization, injection, and audit stages.

#### Scenario: Resolution chain produces audit trail
- **WHEN** a parameter is resolved through the canonical chain
- **THEN** the system SHALL log the source used, any conflicts encountered, and the final resolved value for audit purposes

#### Scenario: Normalization handles type conversion
- **WHEN** a parameter source provides a string value but the target expects a different type
- **THEN** the normalization stage SHALL attempt type conversion and return an error if conversion fails
