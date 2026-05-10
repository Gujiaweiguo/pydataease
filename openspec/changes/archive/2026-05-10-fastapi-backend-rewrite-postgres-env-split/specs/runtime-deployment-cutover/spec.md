## ADDED Requirements

### Requirement: Development topology SHALL support local frontend and backend with Docker PostgreSQL
The migrated system SHALL support a development topology consisting of a locally run frontend, a locally run FastAPI backend, and a Docker-managed PostgreSQL instance.

#### Scenario: Developer starts the local stack
- **WHEN** a developer follows the supported development workflow
- **THEN** the frontend and FastAPI backend SHALL be able to run locally against a Docker PostgreSQL instance

### Requirement: Production topology SHALL support pydataease-app and pydataease-pg
The migrated system SHALL support a production topology centered on Docker `pydataease-app` and Docker `pydataease-pg`, with health checks and environment-variable-driven configuration.

#### Scenario: Production-like deployment starts
- **WHEN** the production compose or installer workflow is executed with valid configuration
- **THEN** `pydataease-app` and `pydataease-pg` SHALL start successfully and pass health validation

### Requirement: Background execution SHALL be isolated from web request handling
The migrated system SHALL provide an isolated background execution model for scheduled and long-running tasks instead of executing all such work inside the FastAPI web request process.

#### Scenario: Long-running task is triggered
- **WHEN** a scheduled or asynchronous task such as export or sync is started
- **THEN** the task SHALL run through the chosen background execution topology without blocking web request handling

### Requirement: Deployment chain SHALL be validated before release
The migrated deployment chain SHALL validate installer behavior, health checks, gateway or WebSocket compatibility requirements in scope, and production-like startup before release approval.

#### Scenario: Production deployment rehearsal runs
- **WHEN** the team executes a production-like deployment rehearsal
- **THEN** installer commands, service health, and in-scope gateway or WebSocket validations SHALL pass before release can proceed

### Requirement: Cutover and rollback SHALL be rehearsed before go-live
The migration SHALL define and rehearse a complete cutover path and a complete rollback path before production release approval.

#### Scenario: Release readiness is evaluated
- **WHEN** the change reaches final release gating
- **THEN** successful cutover rehearsal and successful rollback rehearsal SHALL both exist as release evidence
