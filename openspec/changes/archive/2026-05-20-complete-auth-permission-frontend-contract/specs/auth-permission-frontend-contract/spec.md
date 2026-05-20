## ADDED Requirements

### Requirement: Frontend authorization management endpoints SHALL exist
The Python backend SHALL expose the Java-compatible authorization management routes used by `core/core-frontend/src/api/auth.ts` under `/de2api`, and each route SHALL require a valid `X-DE-TOKEN` unless explicitly whitelisted by existing auth middleware.

#### Scenario: Auth resource routes require authentication
- **WHEN** a request without `X-DE-TOKEN` calls any `/de2api/auth/*` endpoint
- **THEN** the backend SHALL return an authentication failure response and SHALL NOT return permission data

#### Scenario: Auth resource routes are mounted under de2api
- **WHEN** an authenticated user calls `GET /de2api/auth/menuResource`
- **THEN** the backend SHALL route the request to the Python FastAPI backend and SHALL return a wrapped response payload

### Requirement: Menu resource query SHALL return assignable menu permissions
The backend SHALL expose `GET /de2api/auth/menuResource` and return a frontend-compatible menu permission tree containing assignable menu resources and permission points.

#### Scenario: Admin queries menu resources
- **WHEN** an authenticated administrator calls `GET /de2api/auth/menuResource`
- **THEN** the backend SHALL return the menu resources that can be assigned through the permission UI

#### Scenario: Menu resources include permission metadata
- **WHEN** menu resources are returned
- **THEN** each resource node SHALL include enough identity and permission metadata for the frontend to display and submit permission assignments

### Requirement: Business resource query SHALL return assignable resources by flag
The backend SHALL expose `GET /de2api/auth/busiResource/{flag}` and return a frontend-compatible tree or list of assignable business resources for supported flags such as dashboard, screen, dataset, and datasource.

#### Scenario: Admin queries dataset resources
- **WHEN** an authenticated administrator calls `GET /de2api/auth/busiResource/dataset`
- **THEN** the backend SHALL return assignable dataset resources visible to that administrator

#### Scenario: Unsupported business flag is requested
- **WHEN** an authenticated user calls `GET /de2api/auth/busiResource/{flag}` with an unsupported flag
- **THEN** the backend SHALL return a controlled validation error rather than a 500 response

### Requirement: Permission lookup endpoints SHALL return existing grants
The backend SHALL expose lookup endpoints for menu and business permissions and SHALL return current grants for the requested target using existing permission storage.

#### Scenario: Role business permissions are queried
- **WHEN** an authenticated administrator calls `POST /de2api/auth/busiPermission` with a role target
- **THEN** the backend SHALL return the effective or stored business-resource permissions for that role in a frontend-compatible shape

#### Scenario: Role menu permissions are queried
- **WHEN** an authenticated administrator calls `POST /de2api/auth/menuPermission` with a role target
- **THEN** the backend SHALL return the menu permissions for that role in a frontend-compatible shape

### Requirement: Permission save endpoints SHALL persist grants atomically
The backend SHALL expose save endpoints for menu and business permissions and SHALL persist permission changes using existing permission grant models without weakening existing enforcement behavior.

#### Scenario: Business permissions are saved
- **WHEN** an authenticated administrator calls `POST /de2api/auth/saveBusiPer` with valid business permission assignments
- **THEN** the backend SHALL persist those assignments atomically and subsequent permission lookup SHALL reflect the saved grants

#### Scenario: Menu permissions are saved
- **WHEN** an authenticated administrator calls `POST /de2api/auth/saveMenuPer` with valid menu permission assignments
- **THEN** the backend SHALL persist those assignments atomically and subsequent `GET /de2api/menu/query` behavior SHALL remain governed by the effective permission model

#### Scenario: Non-admin attempts to save permissions
- **WHEN** an authenticated user without authorization-management permission calls a save endpoint
- **THEN** the backend SHALL reject the request with an authorization failure and SHALL NOT modify stored grants

### Requirement: Target permission endpoints SHALL support target-specific lookup and save
The backend SHALL expose target-permission endpoints for menu and business resources so the frontend can inspect and update permissions for a specific target type and target id.

#### Scenario: Target business permissions are queried
- **WHEN** an authenticated administrator calls `POST /de2api/auth/busiTargetPermission`
- **THEN** the backend SHALL return business-resource grants for the requested target

#### Scenario: Target menu permissions are saved
- **WHEN** an authenticated administrator calls `POST /de2api/auth/saveMenuTargetPer` with valid target menu grants
- **THEN** the backend SHALL persist those grants and subsequent target permission lookup SHALL reflect the change

### Requirement: User organization option endpoint SHALL support authorization UI selection
The backend SHALL expose `GET /de2api/user/org/option` and return user options usable by the authorization UI for assigning permissions within the current organization context.

#### Scenario: User options are requested
- **WHEN** an authenticated administrator calls `GET /de2api/user/org/option`
- **THEN** the backend SHALL return users available for permission assignment in the current organization context

#### Scenario: Regular user requests user options
- **WHEN** an authenticated user without user-management permission calls `GET /de2api/user/org/option`
- **THEN** the backend SHALL return only data permitted for that user or reject the request with an authorization failure
