## Why

The FastAPI backend already validates JWTs on protected routes, but it cannot mint, refresh, or retire those tokens through the frontend's existing login flow. Adding contract-compatible login authentication now unblocks the Python backend from serving the current UI without forcing auth-flow rewrites.

## What Changes

- Add a persisted community-auth user model, repository surface, and default admin seed for FastAPI.
- Add RSA key management plus a `/de2api/dekey` endpoint so the frontend can encrypt login credentials before submission.
- Add `/de2api/login/localLogin`, `/de2api/login/refresh`, and `/de2api/logout` endpoints with frontend-compatible request and response contracts.
- Modify runtime authentication behavior so issued and validated JWTs can use community-compatible per-user secrets derived from stored credentials.
- Add auth contract coverage for login, refresh, logout, token validation, and default-admin behavior.

## Capabilities

### New Capabilities
- `user-management`: Community user persistence, admin bootstrap data, and password utility behavior required by login auth.
- `login-auth-endpoints`: Login, refresh, logout, and RSA public-key serving contracts used by the existing frontend auth flow.

### Modified Capabilities
- `auth-runtime-compatibility`: JWT validation requirements change from a single global signing secret to compatibility with per-user community token secrets and the login runtime.

## Impact

- New database table: `core_user` with seeded default admin data.
- New backend endpoints: `/de2api/dekey`, `/de2api/login/localLogin`, `/de2api/login/refresh`, `/de2api/logout`.
- Modified auth middleware and token issuance flow in the FastAPI backend.
- New backend dependencies for password hashing and RSA cryptography support.
