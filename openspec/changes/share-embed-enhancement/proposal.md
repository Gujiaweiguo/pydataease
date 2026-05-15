## Why

The backend already has share models (`XpackShare`, `CoreShareTicket`) and CRUD endpoints, but the current implementation is a skeleton — share tokens are not verified at view time, password protection is stored but never enforced, embed-specific tokens (`X-EMBEDDED-TOKEN`) are parsed but not validated against share records, and there is no public access path that allows unauthenticated users to view shared resources. Without these, the share/embed feature is non-functional in the rewritten backend.

## What Changes

- Implement public share resolution: unauthenticated users can access a shared dashboard/chart via a short UUID link, with optional password verification.
- Implement embed token flow: generate and validate `X-EMBEDDED-TOKEN` (signed JWT) that grants scoped read-only access to a specific shared resource, suitable for iframe embedding.
- Enforce share expiration: validate `exp` timestamp on share records and reject expired shares.
- Wire ticket-based access: support `CoreShareTicket` for fine-grained access control (per-ticket access with optional `args` and `access_time` tracking).
- Add share audit: record access events (who accessed what, when) for shared resources.

## Capabilities

### New Capabilities
- `public-share-access`: Unauthenticated resolution of shared resources via UUID, with optional password verification and expiration enforcement.
- `embed-token-auth`: JWT-based embed token generation and validation for iframe-scoped read-only access to shared dashboards and charts.
- `share-audit`: Access event recording for shared resources, tracking ticket usage and access timestamps.

### Modified Capabilities

## Impact

- Affects backend share services and middleware in `core/pydataease-backend/`.
- Requires updates to the auth middleware to allow unauthenticated access on public share routes while still enforcing embed token validation.
- Affects `XpackShare` and `CoreShareTicket` read paths — no schema changes needed, the existing columns are sufficient.
- Gate layer: **L0 backend + L1 backend** (auth/middleware changes require contract test attention). No L2 needed since no new migrations or external services.
