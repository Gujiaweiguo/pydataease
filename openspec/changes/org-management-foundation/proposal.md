## Why

The pydataease backend has user authentication and menu scaffolding but no organization model. In DataEase, organizations are the fundamental tenancy boundary: roles, resources, and permissions all belong to organizations. Without this foundation, user-role binding and permission management cannot proceed.

## What Changes

- Introduce an organization entity (`core_org`) with multi-level tree structure and full CRUD.
- Add user-organization membership so users can belong to one or more organizations.
- Implement current-organization context resolution so that every request after login knows which org the user is operating in.
- Add organization switching API (`/user/switch/{oid}`) and validation.
- Provide system-admin bootstrap with a default/root organization seeded in migration.
- Enforce organization deletion constraints: cannot delete org with children; deleting org cascades to its resources.
- Keep existing login, JWT, and menu-query flows working without regression.

## Plan Context

- **Plan ID**: `pydataease-system-management-roadmap-v1`
- **Plan file**: `.sisyphus/plans/pydataease-system-management-roadmap-v1.md`
- **Depends on**: existing `CoreUser`, JWT, `login` auth infrastructure (no prior OpenSpec change)
- **Followed by**: `user-role-center`
- **Phase in plan**: Phase C — tasks T5 (T1-T4 are cross-cutting research/abstraction phases shared across changes)

## Capabilities

### New Capabilities
- `organization-model`: Organization tree with CRUD, user membership, current-org context, bootstrap, and deletion constraints.

### Modified Capabilities
- `auth-context`: Extend JWT claims and middleware to carry and validate current-organization context.
- `bootstrap-seed`: Add default organization and bind admin user to it during migration.

## Impact

- Affects backend models, repositories, services, and routers in `core/pydataease-backend/`.
- Adds Alembic migration for `core_org` and user-org membership table.
- Extends auth middleware to resolve and validate `oid` from JWT or request.
- Requires existing login flow to continue working unchanged during rollout.
- Verification: L0 backend + L1 backend + L2 backend (new tables, foreign keys, migration).
