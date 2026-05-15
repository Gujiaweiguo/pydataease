## 1. Row Permission Model and Migration

- [ ] 1.1 Create `CoreRowPermission` model with fields: `id`, `dataset_id`, `target_type` (org/role/user/sysvar), `target_id`, `filter_sql`, `enabled`.
- [ ] 1.2 Write Alembic migration with expand-first approach.

## 2. Column Permission Model and Migration

- [ ] 2.1 Create `CoreColumnPermission` model with fields: `id`, `dataset_id`, `field_id`, `target_type` (org/role/user), `target_id`, `action` (disable/desensitize/mask).
- [ ] 2.2 Write Alembic migration with expand-first approach.

## 3. Permission Rule Management API

- [ ] 3.1 Implement CRUD APIs for row-permission rules per dataset.
- [ ] 3.2 Implement CRUD APIs for column-permission rules per dataset.
- [ ] 3.3 Implement whitelist API: exempt specific users from row/column rules.

## 4. Query-Time Enforcement

- [ ] 4.1 Extend SQL execution engine to collect applicable row-permission rules for current user + dataset.
- [ ] 4.2 Inject row filters as WHERE clauses into dataset queries.
- [ ] 4.3 Apply column-permission rules to query results: hide disabled fields, mask/desensitize specified fields.
- [ ] 4.4 Handle priority: user > role > org for conflicting column rules.

## 5. Guardrails and Verification

- [ ] 5.1 Add feature flag to disable row/column injection (fallback to object-level permissions only).
- [ ] 5.2 `cd core/pydataease-backend && uv run ruff check .` — zero errors.
- [ ] 5.3 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass.
- [ ] 5.4 API test: user with row filter sees subset of rows; user with column mask sees desensitized data.
- [ ] 5.5 Whitelist user bypasses row/column rules correctly.
