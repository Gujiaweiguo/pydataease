## Why

With organizations in place, the next layer is user and role management inside orgs. DataEase requires per-org user CRUD, role CRUD, and user-role mounting/unmounting as the foundation for all permission work. The backend currently has only a bare `CoreUser` model with no admin APIs.

## What Changes

- Add user management APIs: list/search/page, create, edit, delete, enable/disable, reset password.
- Add role management APIs: list, create, edit, delete, detail.
- Add user-role binding APIs: mount user to role, unmount user from role, list users in role, list roles for user.
- Enforce org-scoping: all user/role operations happen within the current-org context.
- Handle edge cases: deleting a user's last role across all orgs removes the user; disabled users cannot log in.
- Optionally support user batch import/export if the existing frontend API stubs and official docs confirm it as v1 scope.

## Plan Context

- **Plan ID**: `pydataease-system-management-roadmap-v1`
- **Plan file**: `.sisyphus/plans/pydataease-system-management-roadmap-v1.md`
- **Depends on**: `org-management-foundation`
- **Followed by**: `permission-menu-resource`
- **Phase in plan**: Phase D — task T6

## Capabilities

### New Capabilities
- `user-management`: Full user lifecycle CRUD with org-scoping, search, enable/disable, password reset.
- `role-management`: Role CRUD with org-scoping, built-in vs custom role distinction, user-role binding.

### Modified Capabilities
- `auth-login`: Disabled users must be rejected at login; role-based identity available after auth.

## Impact

- Adds `core_role` and `core_role_user` tables via Alembic migration.
- Adds user, role, and user-role router endpoints in `core/pydataease-backend/app/routers/`.
- Frontend API stubs in `api/user.ts` and `api/auth.ts` map to these endpoints.
- Verification: L0 backend + L1 backend + L2 backend (new tables, foreign keys).
