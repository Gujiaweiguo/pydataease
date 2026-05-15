## Context

The backend already has a complete share data model and CRUD skeleton. `XpackShare` stores `uuid`, `pwd`, `exp`, `auto_pwd`, `ticket_require`, and `resource_id`. `CoreShareTicket` stores per-ticket access with `exp`, `args`, and `access_time`. The `share_service.py` handles create/update/delete for shares and tickets, and the router exposes all endpoints under `/share/`.

What's missing: the share resolution and enforcement logic. When a user (authenticated or not) accesses a shared resource, the system needs to verify the share is valid (not expired, password matches if set), resolve the underlying resource (dashboard or chart), and return its data. The embed token path (`X-EMBEDDED-TOKEN`) is parsed in auth middleware but not validated against share records. Ticket `access_time` is never updated.

The auth middleware already whitelists `/share/proxyInfo` and `/share/validate` for unauthenticated access, and the `X-EMBEDDED-TOKEN` header is already decoded using `share_secret_key`.

## Goals / Non-Goals

**Goals:**
- Enable unauthenticated users to view shared dashboards/charts via UUID link with optional password protection.
- Generate and validate embed tokens for iframe embedding with scoped read-only access.
- Enforce share expiration and ticket-based access control.
- Record access events for audit.

**Non-Goals:**
- New database migrations or schema changes — existing columns are sufficient.
- Frontend changes — this change focuses on backend API activation.
- Share link customization (custom slugs, QR codes).
- Rate limiting on public share endpoints (deferred).
- Share revocation cascade (deleting a dashboard should cascade-delete shares — separate concern).

## Decisions

### 1. Add a `resolve` method to ShareService that enforces all guards

A single `resolve(uuid, password=None)` method will:
1. Look up the share by UUID.
2. Check `exp` against current time — reject if expired.
3. If `pwd` is set, verify the provided password matches — reject if wrong.
4. Update ticket `access_time` if a ticket is involved.
5. Return the share record with the associated `resource_id` and `type`.

**Why:** Centralizing resolution in one method prevents guard-bypass bugs. Every public-facing share endpoint calls this method.

**Alternatives considered:**
- **Separate guard functions per check:** rejected because it's easy to forget one guard in a new endpoint.
- **Middleware-level enforcement:** rejected because share resolution is business logic, not transport-layer concern.

### 2. Generate embed tokens as signed JWTs with resource scope

Embed tokens will be JWTs signed with `DE_SHARE_SECRET_KEY` containing:
- `resourceId`: the shared resource ID
- `exp`: token expiration (derived from the share's `exp`)
- `uuid`: the share UUID

The auth middleware already parses `X-EMBEDDED-TOKEN` and puts `share_resource_id` into request state. We extend this to validate the token against an active share record.

**Why:** JWTs are stateless — no DB lookup needed for every embed request. The existing `share_secret_key` and middleware parsing logic are already in place.

**Alternatives considered:**
- **Opaque tokens with DB lookup:** rejected because embed views are high-frequency and stateless tokens reduce DB load.
- **Reusing the share UUID directly as the embed token:** rejected because UUIDs are short (16 chars) and lack expiration info.

### 3. Add a dedicated public endpoint `/share/view/{uuid}` for unauthenticated resource resolution

This endpoint is added to the auth whitelist and resolves the share to return the underlying visualization data. It accepts an optional `password` query parameter.

**Why:** The existing `/share/proxy/{uuid}` requires authentication. We need a separate public path that the auth middleware allows through.

**Alternatives considered:**
- **Making `/share/proxy/{uuid}` public:** rejected because it's currently used by authenticated users for share management.
- **Using `/share/proxyInfo` for everything:** rejected because it returns share metadata, not the underlying resource data.

### 4. Audit via `access_time` update on tickets, plus a lightweight access log

For ticket-based access, update `CoreShareTicket.access_time` on every access. For non-ticket access, record a minimal log entry with share UUID, timestamp, and client IP.

**Why:** `access_time` already exists on `CoreShareTicket`. For non-ticket access, a simple in-memory counter with periodic DB flush avoids a new table.

**Alternatives considered:**
- **New `core_share_access_log` table:** rejected to avoid a migration; can be added later if audit requirements grow.
- **No audit at all:** rejected because share access tracking is a security requirement.

## Risks / Trade-offs

- **[Risk] Public share endpoints could be abused for resource enumeration** → **Mitigation:** UUIDs are 16-char URL-safe tokens (2^96 entropy). Rate limiting can be added later.
- **[Risk] Embed tokens cached in iframes may outlive share revocation** → **Mitigation:** Embed tokens have short TTL aligned with share `exp`. Middleware validates against the share record on each request for critical operations.
- **[Risk] Password-protected shares need a two-step flow (get share info → submit password)** → **Mitigation:** This matches the DataEase Java backend behavior and is expected by the frontend.
