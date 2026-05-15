## 1. Role Model and Migration

- [x] 1.1 Create `CoreRole` SQLAlchemy model (`core_role` table) with fields: `id`, `name`, `description`, `oid` (org), `type` (built-in=0, custom=1), `create_time`, `update_time`.
- [x] 1.2 Create `CoreRoleUser` association model (`core_role_user` table) linking `role_id` to `user_id` with `oid` scope.
- [x] 1.3 Write Alembic migration for both tables with expand-first approach.
- [x] 1.4 Seed built-in roles: system-admin (global), org-admin (per default org), normal-user (per default org).

## 2. User Management API

- [x] 2.1 Implement `POST /user/pager/{page}/{limit}` — paginated user list with search/filter within current org.
- [x] 2.2 Implement `POST /user/create` — create user with account, name, email, phone, roles, org membership.
- [x] 2.3 Implement `POST /user/edit` — edit user fields (not account); update role bindings.
- [x] 2.4 Implement `POST /user/delete/{uid}` — delete user; validate not last admin.
- [x] 2.5 Implement `POST /user/enable` — enable/disable user; disabled users rejected at login.
- [x] 2.6 Implement `POST /user/resetPwd/{uid}` — reset user password to system default.
- [x] 2.7 Implement `GET /user/queryById/{uid}` — user detail including roles and org memberships.
- [x] 2.8 Implement `GET /user/defaultPwd` — return system default password policy.

## 3. Role Management API

- [x] 3.1 Implement `POST /role/query` — list roles with search within current org.
- [x] 3.2 Implement `POST /role/create` — create custom role inheriting from built-in org role.
- [x] 3.3 Implement `POST /role/edit` — edit custom role name/description.
- [x] 3.4 Implement `GET /role/detail/{rid}` — role detail with member list.
- [x] 3.5 Implement `POST /role/delete/{rid}` — delete custom role; unbind all users; validate not built-in.
- [x] 3.6 Implement `POST /role/user/option` — list users available for role assignment in current org.
- [x] 3.7 Implement `GET /role/searchExternalUser/{keyword}` — search users by account/ID outside current org.

## 4. User-Role Binding API

- [x] 4.1 Implement `POST /role/mountUser` — bind user(s) to role in current org.
- [x] 4.2 Implement `POST /role/unMountUser` — unbind user(s) from role; if last role across all orgs, delete user.
- [x] 4.3 Implement `POST /user/role/selected/{page}/{limit}` — paginated users in a specific role.
- [x] 4.4 Implement `POST /user/byCurOrg` — list users in current org for auth/assignment UI.
- [x] 4.5 Implement `POST /role/byCurOrg` — list roles in current org.

## 5. Verification

- [x] 5.1 `cd core/pydataease-backend && uv run ruff check .` — zero errors.
- [x] 5.2 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass.
- [x] 5.3 `cd core/pydataease-backend && uv run alembic upgrade head` — migration succeeds.
- [x] 5.4 API smoke test: create user → assign role → list users in role → disable user → verify login rejected.
