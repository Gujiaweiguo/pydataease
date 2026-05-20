## Why

The FastAPI backend is missing the relation/lineage endpoints that let callers trace how datasources, dataset groups, and visualizations are connected. Without these APIs, the frontend cannot answer basic impact-analysis questions before editing or deleting analytics assets.

## What Changes

- Add a new authenticated relation router under `/de2api` for datasource, dataset, and visualization lineage lookups.
- Expose `POST /relation/datasource/{id}` to return dataset groups backed by a datasource.
- Expose `POST /relation/dataset/{id}` to return charts that use a dataset group.
- Expose `POST /relation/dv/{id}` to return charts linked to a visualization scene.
- Add backend route registration and focused contract/auth tests for the new endpoints.

## Capabilities

### New Capabilities
- `relation-lineage-api`: Authenticated lineage endpoints that trace datasource → dataset, dataset → chart, and visualization → chart relationships.

### Modified Capabilities
- None.

## Impact

- Affects FastAPI routers and app route registration in `core/pydataease-backend/app/`.
- Uses existing SQLAlchemy models `CoreDatasetTable` and `CoreChartView` for lookup queries.
- Adds backend tests in `core/pydataease-backend/tests/` for route mounting and auth enforcement.
- Verification: L0 backend (`uv run ruff check .`) plus targeted API/auth checks via pytest and import smoke test because this is an authenticated API contract change.
