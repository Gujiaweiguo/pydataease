## ADDED Requirements

### Requirement: The system SHALL provide a unified provider adapter contract for external identity sources
LDAP, OIDC, and CAS SHALL be abstracted into a single provider adapter contract that covers configuration persistence, callback handling, claim mapping, error handling, and local account linkage. No parallel implementation paths are permitted.

#### Scenario: Provider adapter contract defines common interface
- **WHEN** a new identity provider type is added to the system
- **THEN** it SHALL implement the unified provider adapter contract, providing configuration schema, callback handler, claim mapper, and error handler

#### Scenario: LDAP provider implements adapter contract
- **WHEN** an LDAP provider is configured and enabled
- **THEN** it SHALL authenticate users through the adapter contract, mapping LDAP attributes to local user fields via declarative claim mapping

#### Scenario: OIDC provider implements adapter contract
- **WHEN** an OIDC provider is configured and enabled
- **THEN** it SHALL handle the OAuth2/OIDC flow through the adapter contract, including callback, token exchange, and claim extraction

#### Scenario: CAS provider implements adapter contract
- **WHEN** a CAS provider is configured and enabled
- **THEN** it SHALL validate service tickets through the adapter contract and map CAS attributes to local user fields

### Requirement: The system SHALL support declarative claim mapping from provider to local users
Admin-configurable mapping rules SHALL translate external identity claims (username, email, organization, roles) into local user and organization structures.

#### Scenario: Admin configures username mapping
- **WHEN** an admin defines a mapping rule that links an external provider's `uid` attribute to the local username field
- **THEN** users authenticating through that provider SHALL have their local username populated from the mapped claim

#### Scenario: Admin configures organization mapping
- **WHEN** an admin defines a mapping rule that links an external provider's group attribute to a local organization
- **THEN** users authenticating through that provider SHALL be placed in the mapped organization

#### Scenario: Missing claim does not block authentication
- **WHEN** a mapped claim is absent from the external provider's response
- **THEN** the system SHALL handle the absence gracefully, using a fallback value or local-default, and SHALL NOT crash

### Requirement: The system SHALL handle provider errors with local account fallback
When an external provider fails (unreachable, timeout, configuration error), the system SHALL fall back to local login without data loss or session disruption.

#### Scenario: Provider unreachable triggers fallback
- **WHEN** an external provider endpoint is unreachable during authentication
- **THEN** the system SHALL log the error and present local login as the fallback option

#### Scenario: Provider configuration error triggers fallback
- **WHEN** an external provider's configuration is invalid or incomplete
- **THEN** the system SHALL disable the provider automatically and present local login as the fallback

### Requirement: The system SHALL NOT depend on de-xpack/ for provider implementation
All provider adapter implementations SHALL work without `de-xpack/` submodule contents. The implementation boundary SHALL be explicitly defined with deferred items listed.

#### Scenario: Provider works without de-xpack
- **WHEN** the `de-xpack/` submodule is not present
- **THEN** all provider adapter contract functionality SHALL still work, using local implementations and mock providers

#### Scenario: Mock provider available for testing
- **WHEN** the system is configured with the test/mock provider
- **THEN** end-to-end authentication flows SHALL be verifiable without any external identity service
