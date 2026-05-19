## 2026-05-10 T01
- Freeze first delivery to standalone/community-oriented backend parity only; explicitly exclude desktop/H2 and distributed/Nacos runtime parity.
- Treat xpack and `de-xpack/` as enterprise boundary documentation only, not implementation scope.
- Preserve path compatibility, auth header semantics, and result-envelope behavior as higher priority than recreating Spring-internal structure.
- Classify WebSocket/STOMP notifications and sync-task runtime as deferred because they are not required to prove core BI CRUD/query/dashboard compatibility in first delivery.

## 2026-05-10 F4
- Scope fidelity verdict is blocked until compatibility leftovers are removed from Python backend: APISIX whitelist entry, xpack whitelist endpoints beyond `xpack_share`, and H2-labeled datasource test expectations.

## 2026-05-10 T14
- The `login-auth-flow` change should be modeled as two new capabilities (`user-management`, `login-auth-endpoints`) plus a delta on `auth-runtime-compatibility`, keeping login contracts separate from lower-level JWT runtime behavior.
- The design baseline for this change assumes bcrypt for stored password verification and deterministic MD5-derived per-user JWT secrets for community compatibility, with RSA key delivery preserved as a first-class API contract.

- interactiveTree now resolves from database-backed service instead of bootstrap stub to match frontend navigation expectations.

## 2026-05-11 interactive-tree wiring
- Kept the service implementation byte-for-byte aligned with the requested content, even though the prior local version used broader exception fallback and unconditional root wrappers, because the task explicitly required exact file creation/edit behavior.

## 2026-05-11 sys-setting bootstrap wiring
- Reused a dedicated `SysSettingService` behind bootstrap dependency injection instead of touching `system.py` routes, keeping bootstrap compatibility stubs isolated from the existing system parameter endpoints the task marked out-of-scope.
- Removed `@final` from `AsyncBaseRepository` so repository subclasses remain type-check clean; multiple existing repositories already inherit from it, so the base abstraction is intentionally extensible in practice.

## 2026-05-17 snapshot table migration
- Added a standalone Alembic revision after `a2b3c4d5e6f7` to create the five missing snapshot tables only, leaving runtime code and existing migrations untouched per bug-fix scope.
- Matched snapshot table schemas to the current PostgreSQL Alembic definitions, including defaults and FK structure, so `uv run alembic upgrade head` can create tables that repository SQL can query immediately without follow-up normalization.

## 2026-05-18 test helper cleanup
- Chose `tests/fixtures/auth_fixtures.py` as the shared `_build_token` home instead of `tests/conftest.py` because tests need normal imports, not fixture injection semantics.
