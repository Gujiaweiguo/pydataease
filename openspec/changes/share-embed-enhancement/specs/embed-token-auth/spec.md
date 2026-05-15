## Requirements

### R1: Embed token generation
The system MUST provide an endpoint that generates a JWT embed token for a given share UUID. The token MUST be signed with `DE_SHARE_SECRET_KEY` and contain `resourceId`, `uuid`, and `exp` claims.

### R2: Embed token validation in middleware
The auth middleware MUST validate `X-EMBEDDED-TOKEN` headers by decoding the JWT with `DE_SHARE_SECRET_KEY`, checking expiration, and verifying the referenced share record exists and is not expired.

### R3: Scoped read-only access
Embed tokens MUST grant read-only access to the shared resource only. Embed token holders MUST NOT be able to modify, delete, or access any other resources.

### R4: Token expiration alignment
Embed token expiration MUST NOT exceed the share's `exp` value. If the share has no expiration, the embed token MUST use a default TTL of 24 hours.

### R5: Share revocation invalidation
If a share is deleted, any previously issued embed tokens for that share MUST be rejected on the next validation attempt (checked against the share record in DB).
