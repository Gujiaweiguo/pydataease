## 1. Foundation

- [x] 1.1 L1: Add the `core_user` SQLAlchemy model, repository interfaces, and Alembic migration that creates the table with bigint IDs, auth fields, and timestamps.
- [x] 1.2 L2: Implement RSA key management that generates or loads a stable backend keypair and exposes the public key retrieval path used by `/de2api/dekey`.
- [x] 1.3 L3: Add password utilities for bcrypt hash/verify plus deterministic MD5-based JWT secret derivation from persisted credential material.

## 2. Auth Endpoints

- [x] 2.1 L4: Implement `POST /de2api/login/localLogin` request/response schemas, RSA credential decryption, community user verification, and JWT issuance with `uid`/`oid` claims.
- [x] 2.2 L5: Implement `GET /de2api/login/refresh` to validate the current `X-DE-TOKEN`, honor the `time` query parameter contract, and reissue session metadata for the authenticated user.
- [x] 2.3 L6: Implement `GET /de2api/logout` as a wrapped community-compatible no-op endpoint and add `GET /de2api/dekey` for RSA public-key delivery.

## 3. Runtime Integration

- [x] 3.1 L7: Update auth middleware and auth dependencies to resolve users from JWT claims, derive per-user signing secrets, and preserve compatible failures for invalid or disabled-user tokens.
- [x] 3.2 L8: Seed the default admin account through migration/bootstrap logic so fresh environments can authenticate with the expected community credentials.

## 4. Verification

- [x] 4.1 L9: Replace the skipped auth contract tests with coverage for `/dekey`, login success/failure, refresh success/failure, logout, and protected-route JWT validation using the new per-user secret model.
