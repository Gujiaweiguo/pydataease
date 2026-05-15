## Context

The FastAPI backend already exposes JWT-protected APIs behind `X-DE-TOKEN`, but it currently assumes a single global signing secret and has no persisted user store or login endpoints. The existing frontend expects the Java community-edition contract: fetch an RSA public key from `/dekey`, encrypt username and password, call `POST /login/localLogin`, store `token/exp/time`, and refresh through `GET /login/refresh?time=...` before expiry. This change must preserve those client contracts while fitting the Python service's layered architecture, response wrapper, and PostgreSQL/Alembic stack.

## Goals / Non-Goals

**Goals:**
- Add a minimal community-auth user domain for the FastAPI backend, including a seeded default admin account.
- Support frontend-compatible RSA-assisted login, token refresh, logout, and public-key discovery endpoints.
- Preserve protected-route auth behavior while changing JWT signing and verification to use per-user compatibility secrets.
- Define implementation boundaries that let auth tests validate the migrated contract end to end.

**Non-Goals:**
- Reproduce enterprise/de-xpack authentication behavior such as per-tenant auth plugins, MFA enforcement, or LDAP implementation.
- Deliver share-link or embedded-token feature parity beyond the already documented runtime compatibility scope.
- Introduce a general-purpose user administration UI or non-auth profile management APIs in this change.

## Decisions

### 1. Persist community users in `core_user` and seed a single default admin
Use a new `core_user` table with bigint IDs, `account`, `name`, `email`, `password_hash`, `enable`, `oid`, `origin`, and timestamps so the Python backend has a durable auth source. Seed the default `admin` account in the migration to match current product expectations and bootstrap first login without separate setup.

**Why:** the middleware cannot derive per-user JWT secrets or validate credentials without stored user data.

**Alternatives considered:**
- Hardcode admin credentials in settings: rejected because token verification needs persisted user state and password changes would not survive deploys.
- Reuse an unrelated table later: rejected because auth needs an explicit, stable contract now.

### 2. Store passwords with bcrypt while deriving JWT secrets from MD5 of the stored hash input
Persist passwords using bcrypt for login verification, then derive the community-compatible JWT signing secret from an MD5 digest tied to the stored credential material for that user. Centralize hashing, verification, and secret derivation in password utilities so login issuance and middleware validation share one rule.

**Why:** bcrypt protects stored credentials, while MD5-based derivation preserves the Java community-edition token shape expectation that secrets are user-specific and credential-derived.

**Alternatives considered:**
- Sign JWTs with the global `settings.secret_key`: rejected because it breaks compatibility requirements for per-user validation.
- Store plaintext passwords for exact Java parity: rejected as an unnecessary security regression.

### 3. Manage RSA keys as backend-owned runtime material with a stable public endpoint
Generate or load one backend RSA key pair on first run, keep the private key server-side, and expose the public key through `GET /de2api/dekey` in the format expected by the frontend. The design allows implementation to persist key material in a dedicated table or controlled file-backed storage, but the contract requires stability across restarts until rotated intentionally.

**Why:** the frontend already encrypts login credentials and expects the backend to decrypt them before verification.

**Alternatives considered:**
- Drop RSA and accept plaintext over TLS: rejected because it breaks the current frontend contract.
- Generate a new keypair per request: rejected because clients fetch and cache a public key independently of login submission timing.

### 4. Implement login and refresh as thin routers over auth services
Route handlers should only validate request shape and return wrapped responses. Auth services will decrypt RSA payloads, load the user, verify credentials and enabled state, issue JWTs with `uid` and `oid` claims, and reissue tokens during refresh after validating the current `X-DE-TOKEN`. Refresh should preserve the frontend contract by accepting the `time` query parameter even if issuance logic only uses it for compatibility and observability.

**Why:** this fits the existing router → service → repository architecture and keeps cryptography and token logic testable.

**Alternatives considered:**
- Put token logic directly in middleware or routers: rejected because it couples HTTP concerns with auth internals and makes testing harder.

### 5. Extend auth middleware to resolve users before verifying JWT signatures
For protected routes, middleware/dependencies should decode token claims enough to identify `uid` and `oid`, load the user, derive that user's signing secret, and then perform full JWT verification. Failure paths must still return compatibility-safe auth errors through the existing response model.

**Why:** per-user secrets mean signature validation can no longer happen with a single static key.

**Alternatives considered:**
- Maintain a secondary global verifier for legacy tokens indefinitely: rejected because it weakens the migration target and complicates runtime rules.

## Risks / Trade-offs

- **[RSA key persistence mismatch]** → Mitigation: define one durable storage strategy during implementation and add startup checks so existing encrypted login flows are not broken by restart-driven key churn.
- **[Community compatibility vs. stronger credential storage]** → Mitigation: isolate secret-derivation rules in one utility and cover token issuance/validation with contract tests to ensure bcrypt storage does not break runtime verification.
- **[Default admin bootstrap risk]** → Mitigation: seed only when absent, require configurable password rotation after deployment, and document rollback/reset steps.
- **[Refresh endpoint semantic drift]** → Mitigation: keep the `time` parameter in the API contract and test the frontend-triggered refresh path rather than optimizing it away.
- **[Existing protected routes depending on current JWT behavior]** → Mitigation: add compatibility tests for both successful and rejected token flows before switching middleware logic.

## Migration Plan

1. Add the `core_user` schema and seed the default admin account.
2. Introduce password utilities and RSA key management primitives behind services/repositories.
3. Implement `/dekey`, `/login/localLogin`, `/login/refresh`, and `/logout` with wrapped responses.
4. Update JWT issuance and verification to use per-user derived secrets.
5. Run auth contract tests covering login, refresh, protected routes, and logout behavior.

Rollback:
- Disable new routes and revert middleware/auth service changes if token validation fails in staging.
- Restore the prior global-secret auth path in code and roll back the migration if user persistence must be removed before release.

## Open Questions

- Should RSA key material live in a dedicated database table for cluster consistency, or in managed file storage with deployment volume guarantees?
- Does the Python backend need to return any placeholder MFA structure in `localLogin` responses for frontend compatibility when MFA is not supported?
- Should refresh reject disabled users immediately even when their current token is otherwise valid, or mirror Java community behavior more loosely?
