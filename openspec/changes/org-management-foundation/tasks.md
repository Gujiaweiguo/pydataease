## 1. Domain Model and Migration

- [x] 1.1 Create `CoreOrg` SQLAlchemy model (`core_org` table) with fields: `id`, `pid`, `name`, `create_time`, `update_time`.
- [x] 1.2 Create user-org membership table/model (`core_user_org` or similar) linking `user_id` to `org_id`.
- [x] 1.3 Write Alembic migration creating both tables with expand-first approach.
- [x] 1.4 Seed a default root organization and bind admin user (id=1) to it in migration.

## 2. Organization CRUD API

- [x] 2.1 Implement `POST /org/page/tree` — return org tree filtered by user membership.
- [x] 2.2 Implement `POST /org/page/create` — create org (optionally under parent); validate parent exists.
- [x] 2.3 Implement `POST /org/page/edit` — rename org.
- [x] 2.4 Implement `POST /org/page/delete/{oid}` — delete org only if no children exist; cascade resource cleanup warning.
- [x] 2.5 Implement `GET /org/resourceExist/{oid}` — check if org has resources before delete.

## 3. Current-Org Context and Switching

- [x] 3.1 Extend auth middleware to resolve current-org from JWT `oid` claim and validate user still belongs to that org.
- [x] 3.2 Implement `POST /user/switch/{oid}` — switch current-org for user (validate membership, issue updated token).
- [x] 3.3 Extend `GET /user/info` response to include current-org info and list of user's org memberships.
- [x] 3.4 Implement `POST /org/mounted` — list orgs available to current user (for org picker).

## 4. Bootstrap and Guardrails

- [x] 4.1 Ensure system admin (account=`admin`) can access all orgs regardless of membership.
- [x] 4.2 Add feature flag / route gate so org CRUD endpoints can be disabled without breaking existing login.
- [x] 4.3 Verify existing login, `/menu/query`, `/login/refresh` flows are not regressed.

## 5. Verification

- [x] 5.1 `cd core/pydataease-backend && uv run ruff check .` — zero errors.
- [x] 5.2 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass.
- [x] 5.3 `cd core/pydataease-backend && uv run alembic upgrade head` — migration succeeds.
- [x] 5.4 API smoke test: create org → list tree → switch org → delete org (no children) works via curl.
