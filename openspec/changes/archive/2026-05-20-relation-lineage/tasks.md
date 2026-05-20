## 1. Relation Router

- [x] 1.1 Create `app/routers/relation.py` with authenticated datasource, dataset, and visualization lineage endpoints.
- [x] 1.2 Register the relation router in `app/main.py` under the existing `/de2api` API prefix.

## 2. Contract Coverage

- [x] 2.1 Add `tests/test_relation_routes.py` to verify all three relation paths are mounted.
- [x] 2.2 Add auth-failure tests proving each relation endpoint rejects unauthenticated requests.

## 3. Verification

- [x] 3.1 Run `cd core/pydataease-backend && uv run ruff check .`.
- [x] 3.2 Run `cd core/pydataease-backend && uv run pytest tests/test_relation_routes.py -v`.
- [x] 3.3 Run `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`.
