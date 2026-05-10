## ADDED Requirements

### Requirement: Migration scope SHALL be frozen before implementation proceeds
The system change process SHALL freeze the migration scope, compatibility matrix, and non-goals before any implementation wave begins, and SHALL treat the latest `.sisyphus/plans/*.md` Plan v1 as the planning source of truth.

#### Scenario: Scope baseline is created before execution
- **WHEN** the change enters implementation readiness
- **THEN** the change SHALL contain a scope baseline that identifies must-keep compatibility, deferred capabilities, and excluded capabilities

### Requirement: First delivery SHALL exclude unapproved runtime profiles
The first delivery SHALL NOT implicitly include desktop/H2 or distributed/Nacos runtime parity unless those profiles are explicitly approved as a controlled scope expansion.

#### Scenario: Unapproved profile parity is detected
- **WHEN** an execution artifact introduces desktop/H2 or distributed/Nacos support without an approved scope expansion
- **THEN** the change SHALL be treated as out of scope and SHALL fail scope validation

### Requirement: Plan and OpenSpec SHALL remain synchronized
The OpenSpec change SHALL derive from the latest Plan v1 and SHALL NOT maintain a separate independent execution plan with conflicting task order, acceptance criteria, or rollback behavior.

#### Scenario: OpenSpec artifacts diverge from Plan v1
- **WHEN** proposal, design, specs, or tasks contradict the latest Plan v1 on task IDs, dependency order, acceptance criteria, or rollback plans
- **THEN** the change SHALL be corrected by resynchronizing to Plan v1 before implementation continues
