## Requirements

### R1: Public share resolution via UUID
The system MUST provide a public (unauthenticated) endpoint that resolves a share UUID to the underlying resource. The endpoint MUST return the visualization data (dashboard or chart) without requiring login.

### R2: Password verification
When a share has a `pwd` value set, the system MUST require the correct password before returning resource data. The password MUST be compared using constant-time comparison to prevent timing attacks.

### R3: Expiration enforcement
The system MUST reject access to shares where `exp` is set and the current time exceeds `exp`. Expired shares MUST return a clear error indicating the share has expired.

### R4: Auto-password support
When `auto_pwd` is `True`, the system MUST auto-generate a random password when the share is created. The creator can retrieve the auto-generated password; viewers must provide it.

### R5: Share type routing
The system MUST use the `type` field (dashboard=0, chart=1, etc.) to route resolution to the correct underlying service (visualization or chart).

### R6: Whitelist integration
The public share endpoint MUST be added to the auth middleware whitelist so unauthenticated requests are not rejected.
