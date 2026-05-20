## Why

The Python/FastAPI backend is missing 13 API endpoints that the frontend already calls. These cover dataset data preview, field enum value lookups, chart field CRUD, chart data drill-down, and dataset detail export. Without them, the BI tool cannot show data in tables, populate filter dropdowns, manage chart custom fields, support drill-down interactions, or export chart data. The frontend is blocked on every core user workflow.

## What Changes

- Add 5 dataset data endpoints: `previewData`, `enumValue`, `enumValueObj`, `enumValueDs`, `getFieldTree`
- Add 4 chart field endpoints: `listByDQ`, `copyField`, `deleteField`, `deleteFieldByChart`
- Add 3 chart data endpoints: `getFieldData`, `getDrillFieldData`, `checkSameDataSet`
- Add 1 dataset export endpoint: `innerExportDataSetDetails`
- Wire all 13 endpoints through the existing 4-layer pattern (router, service, repository, model)
- Reuse existing SQL execution engine and dataset/chart services where applicable

## Capabilities

### New Capabilities
- `dataset-data-preview`: Dataset data preview, enum value lookups, field tree retrieval, and dataset detail export (6 endpoints under `/datasetData/`)
- `chart-field-ops`: Chart field listing by dimension/quota, copying fields, and deleting custom fields (4 endpoints under `/chart/`)
- `chart-data-enumeration`: Chart field enumeration data, drill-down data, and same-dataset checks (3 endpoints under `/chartData/` and `/chart/`)

### Modified Capabilities
<!-- No existing spec-level requirement changes. These are new endpoints added to existing routers. -->

## Impact

- **Routers**: `app/routers/dataset.py` gains 6 new routes; `app/routers/chart.py` gains 7 new routes (4 chart field + 2 chart data + 1 same-dataset check)
- **Services**: `app/services/dataset_service.py` and `app/services/chart_service.py` grow new methods; may need a new `chart_field_service.py` for chart field operations
- **Repositories**: New repository methods for field tree queries, enum value queries, and chart field CRUD
- **Models**: No new database tables expected; chart custom fields likely stored in existing chart field tables
- **API contract**: All endpoints follow existing `/de2api` prefix, `ResultMessage` response wrapper, and `X-DE-TOKEN` auth
- **Dependencies**: Relies on existing SQL execution engine (`sql-execution-engine` spec) and dataset/table infrastructure
- **Testing gate**: L0 backend (ruff) + L1 backend (pytest) — these are internal API logic changes, no database schema changes, no frontend code changes
