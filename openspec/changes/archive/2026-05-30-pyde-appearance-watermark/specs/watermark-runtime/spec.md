## ADDED Requirements

### Requirement: Watermark configuration SHALL be manageable by admins
The backend SHALL provide authenticated admin-only endpoints for saving and querying watermark configuration, including global enable/disable, text template, font settings, and display scope.

#### Scenario: Admin saves watermark configuration
- **WHEN** an admin sends a write request to `/watermark/save` with a valid configuration payload
- **THEN** the backend SHALL persist the watermark configuration and return a wrapped success response

#### Scenario: Non-admin cannot save watermark configuration
- **WHEN** a non-admin user sends a write request to `/watermark/save`
- **THEN** the backend SHALL return a 403 response

#### Scenario: Public query returns limited watermark fields
- **WHEN** an unauthenticated client queries `/watermark/find`
- **THEN** the backend SHALL return only the fields needed for runtime display (enable status, text template, opacity), without exposing admin-only metadata

### Requirement: Watermark SHALL display according to context-specific rules
Watermark visibility SHALL vary by viewing context: normal pages (logged-in users), share pages (public access), and embedded pages (with or without login state).

#### Scenario: Watermark displays on normal page for logged-in user
- **WHEN** a logged-in user views a normal dashboard page and watermark is enabled
- **THEN** the watermark overlay SHALL be rendered according to the saved configuration

#### Scenario: Watermark displays on share page
- **WHEN** a public user views a shared dashboard and watermark is enabled for share context
- **THEN** the watermark overlay SHALL be rendered on the shared page

#### Scenario: Watermark displays on embedded page
- **WHEN** an embedded page is loaded and watermark is enabled for embed context
- **THEN** the watermark overlay SHALL be rendered in the embedded iframe

#### Scenario: Watermark disabled for specific context
- **WHEN** watermark is globally enabled but disabled for the share page context
- **THEN** shared pages SHALL NOT render the watermark overlay

### Requirement: Watermark text SHALL support system variable placeholders
Watermark text templates SHALL support placeholder syntax that resolves to system variable values at runtime.

#### Scenario: Watermark text resolves system variable placeholder
- **WHEN** the watermark text template contains a system variable placeholder (e.g., `${currentUser}`)
- **AND** a logged-in user views a watermarked page
- **THEN** the placeholder SHALL be resolved to the current user's name in the rendered watermark

#### Scenario: Unresolvable placeholder falls back gracefully
- **WHEN** the watermark text template contains a placeholder that cannot be resolved (e.g., no login context on a public share page)
- **THEN** the placeholder SHALL be replaced with an empty string or a configured fallback value

### Requirement: Watermark feature flag SHALL support safe rollback
Disabling the watermark feature flag SHALL turn off all watermark display without deleting saved configuration.

#### Scenario: Disabling watermark flag stops display
- **WHEN** the watermark feature flag is disabled
- **THEN** no watermark SHALL be rendered on any page context
- **AND** saved watermark configuration SHALL remain in storage for future re-enablement
