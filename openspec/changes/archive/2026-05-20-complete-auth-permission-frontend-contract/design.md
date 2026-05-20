## Context

The active Python backend already has identity authentication, menu filtering, resource authorization, row/column permissions, and permission storage models. The remaining gap is the frontend-facing authorization management contract used by `core/core-frontend/src/api/auth.ts`: administrators can request permission trees and save menu/business-resource grants through `/auth/*` endpoints in the legacy Java backend, but the Python backend does not yet expose equivalent routes.

This change completes the configuration side of the permission loop. It does not replace the existing enforcement layer; it provides API compatibility so the shared Vue frontend can configure the permissions that enforcement already consumes.

## Goals / Non-Goals

**Goals:**
- Expose the frontend-compatible `/auth/*` permission management API surface in FastAPI.
- Reuse existing permission models and effective-permission behavior rather than creating a second permission system.
- Preserve `X-DE-TOKEN` authentication and `ResultMessage` response wrapping for all new routes.
- Provide contract tests for route existence, authentication behavior, response shape, and basic save/read flows.

**Non-Goals:**
- Redesign menu filtering, resource enforcement, or row/column permissions.
- Add XPack-only authorization providers, SSO role synchronization, or external IAM integration.
- Change frontend API paths or request names.
- Introduce new permission tables unless implementation proves an existing table cannot represent the Java-compatible contract.

## Decisions

1. **Use a new `auth` router for frontend contract compatibility.**
   - Decision: add `app/routers/auth.py` with prefix `/auth` and include it under `/de2api`.
   - Rationale: the frontend already imports `api/auth.ts` and expects `/auth/*` paths. Matching those paths avoids frontend changes and isolates admin permission management from login/authentication routes.
   - Alternative considered: add these routes to `login.py` or `system.py`; rejected because the endpoints manage authorization grants, not authentication or system settings.

2. **Reuse existing permission catalog and grant models.**
   - Decision: implement service/repository behavior over existing permission point and grant models (`CorePermissionPoint`, `CoreRolePermission`, `CoreUserPermission`, `CoreOrgPermission`) where possible.
   - Rationale: existing menu/resource enforcement already depends on these concepts. Duplicating permission storage would make enforcement and configuration drift.
   - Alternative considered: create Java-shaped compatibility tables; rejected unless an implementation spike proves unavoidable.

3. **Separate permission management from permission enforcement.**
   - Decision: this change adds read/write APIs for permission assignment but does not change how resource routers enforce permissions.
   - Rationale: enforcement is already covered by existing specs and tests. Keeping this change focused reduces regression risk.
   - Alternative considered: combine enforcement corrections into this change; rejected because it would blur scope and duplicate `permission-menu-resource` / `permission-row-column` work.

4. **Return frontend-compatible trees and grant payloads, not internal ORM shapes.**
   - Decision: schemas for resource trees, menu trees, target permission lookup, and save payloads should be explicit Pydantic DTOs with camelCase compatibility.
   - Rationale: the frontend contract is path- and shape-sensitive. Explicit schemas make compatibility testable and avoid leaking backend storage details.

5. **Treat `GET /user/org/option` as part of this contract.**
   - Decision: implement user-option lookup needed by the authorization UI in the same change.
   - Rationale: `api/auth.ts` calls this endpoint alongside `/auth/*`; without it, the permission UI remains incomplete.

## Risks / Trade-offs

- **Risk: Existing permission tables may not map exactly to Java payloads.** → Mitigation: define DTOs from frontend needs, transform at service boundaries, and only add migration work if mapping is impossible.
- **Risk: Permission save APIs could accidentally weaken enforcement.** → Mitigation: keep enforcement code untouched except through existing repositories; add tests that verify unauthorized requests still return 401/403.
- **Risk: Admin-only APIs may be exposed to regular users.** → Mitigation: require authenticated admin/manage authorization for save endpoints and test non-admin rejection.
- **Risk: Resource tree responses become too broad or too expensive.** → Mitigation: build trees from existing menu/resource catalog and existing resource repositories; paginate only if the frontend contract supports it.
- **Risk: Existing OpenSpec changes already claim permission tasks are complete.** → Mitigation: scope this change as frontend contract completion, not enforcement completion, and update contract tests to prove route parity.

## Migration Plan

1. Add router/service/schema/repository code for the `/auth/*` and `/user/org/option` contract.
2. Reuse existing permission records; add migration only if a required persisted field is missing.
3. Add contract tests and permission-management service tests.
4. Run required gates:
   - `cd core/pydataease-backend && uv run ruff check .`
   - `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
   - `cd core/pydataease-backend && uv run alembic upgrade head` only if migrations are added.
5. Rollback by disabling/removing the new router registration; no frontend change is required.

## Open Questions

- Which permission target types must be writable in the first implementation: role, user, org, or all three?
- Should save endpoints replace all grants for a target atomically, or apply incremental updates?
- Does the frontend expect grant denial semantics, or only positive grants?
