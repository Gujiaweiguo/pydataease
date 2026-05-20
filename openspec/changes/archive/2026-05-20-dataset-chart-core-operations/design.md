## Context

The Python/FastAPI backend (`core/pydataease-backend/`) implements a 4-layer architecture: Router → Service → Repository → Model. The frontend (Vue, `core/core-frontend/src/api/dataset.ts` and `chart.ts`) already calls 13 API endpoints that the Python backend does not yet serve. The Java legacy backend implements these, and the Python backend must provide compatible replacements.

The existing codebase already has:
- `dataset.py` router with 16 endpoints, `chart.py` router with 10 endpoints, `dataset_field.py` router with 8 endpoints
- `DatasetService`, `ChartService`, `ChartDataBuilder` service layer
- Repository layer with `DatasetFieldRepository` (already has `list_checked_by_group`, `list_checked_by_group_no_chart_filter`, `delete_by_id`, `delete_by_chart_id`, `save_field`)
- Models: `CoreDatasetTableField` (with `chart_id` column for chart-specific custom fields), `CoreChartView`
- SQL execution via `SQLExecutor` / `DatasourceService` for external datasource queries

Key observation: Several chart-field endpoints under `/chart/` share functionality with existing `/datasetField/` routes but differ in path contract (e.g., `/chart/listByDQ/{id}/{chartId}` takes two path params vs `/datasetField/listByDQ/{id}` which takes one). The chart routes operate on `CoreDatasetTableField` rows filtered by `chart_id`.

## Goals / Non-Goals

**Goals:**
- Implement all 13 missing endpoints so the frontend can function end-to-end
- Follow the existing 4-layer pattern exactly (router → service → repo → model)
- Maintain API contract compatibility with the frontend's existing request/response shapes
- Reuse existing repository methods where chart routes delegate to the same data operations

**Non-Goals:**
- Refactoring existing endpoints or changing established patterns
- Adding new database tables or Alembic migrations (all models/columns already exist)
- Frontend changes (the frontend already calls these endpoints)
- Implementing the full Java export pipeline (export endpoint can return a stub initially if the async export infrastructure is not yet complete)

## Decisions

### D1: Chart field routes live in `chart.py` router, not `dataset_field.py`

**Decision**: Add the 4 chart-field endpoints (`listByDQ`, `copyField`, `deleteField`, `deleteFieldByChart`) to the existing `chart.py` router under `/chart/` prefix.

**Rationale**: The frontend calls these under `/chart/`, not `/datasetField/`. Keeping them in `chart.py` maintains URL contract compatibility. The underlying service can still use `DatasetFieldRepository` for data access.

**Alternative**: Add them to `dataset_field.py` with a different route prefix — rejected because it would require frontend URL changes.

### D2: Dataset data endpoints go in `dataset.py` router under `/datasetData/`

**Decision**: Add the 6 dataset-data endpoints (`previewData`, `enumValue`, `enumValueObj`, `enumValueDs`, `getFieldTree`, `innerExportDataSetDetails`) to `dataset.py` router.

**Rationale**: The existing `dataset.py` router already handles `/datasetData/tableField`, `/datasetData/getDatasetTotal`, `/datasetData/previewSql`. The new endpoints follow the same URL pattern and service delegation.

### D3: Chart data enumeration endpoints go in `chart.py` router

**Decision**: Add `getFieldData`, `getDrillFieldData`, `checkSameDataSet` to `chart.py` router. The first two under `/chartData/` prefix, the third under `/chart/`.

**Rationale**: Matches the frontend's URL paths. The `chart.py` router already has `/chartData/getData` and `/chartData/innerExportDetails`.

### D4: Service layer — extend existing services, no new service files

**Decision**: Add methods to `DatasetService` (for dataset data ops) and `ChartService` (for chart field + chart data ops). Do not create separate `ChartFieldService`.

**Rationale**: The operations are tightly coupled to existing service logic (dataset SQL execution, chart data building). A separate service would require cross-service coordination that adds complexity without benefit for 13 endpoints.

### D5: Enum value queries use the SQL execution engine

**Decision**: `enumValue`, `enumValueObj`, `enumValueDs`, `getFieldData`, `getDrillFieldData` all build `SELECT DISTINCT <field> FROM <base_sql>` or similar queries and execute them through the existing `SQLExecutor` / datasource connection pattern.

**Rationale**: The existing `preview_sql()` and `get_data()` methods already demonstrate the pattern: resolve datasource → build SQL → execute → transform. Enum queries are a simpler variant of the same flow.

### D6: `previewData` reuses the chart data execution pipeline

**Decision**: `previewData` resolves the dataset group's base SQL, applies pagination (limit/offset from request), executes against the datasource, and returns rows + field metadata. This is similar to `chart_service.get_data()` but without chart aggregation.

**Rationale**: The dataset preview is a direct table scan with pagination, not a chart aggregation. It can share the datasource resolution logic but skip the chart SQL builder.

### D7: `innerExportDataSetDetails` delegates to export infrastructure

**Decision**: Implement this endpoint by resolving the chart's dataset, executing the chart query (similar to `get_data`), and returning the data in the export format. If the async export worker infrastructure is not fully wired, return a synchronous response initially.

**Rationale**: The frontend calls this from the chart context to export the underlying dataset. The data execution is identical to chart data retrieval; the difference is output format.

### D8: Permission checks follow existing patterns

**Decision**: Dataset data endpoints use `perm.require_resource_access(user, "dataset", "use")`. Chart endpoints use `get_current_user` auth only (matching existing chart routes which don't do resource-level permission checks).

**Rationale**: Consistency with existing endpoints in the same routers.

## Risks / Trade-offs

- **[Java API contract divergence]** → The frontend was built against the Java backend's response shapes. If the Python responses differ in field names or nesting, the frontend will break. **Mitigation**: Match the exact response shapes by examining the frontend's consumption of each response. Use `serialization_alias` for camelCase compatibility.

- **[Enum query performance]** → `SELECT DISTINCT` on large tables can be slow. **Mitigation**: Add `LIMIT` clause (default 100 or configurable) to enum queries, matching the Java backend's behavior.

- **[Chart custom field isolation]** → Chart custom fields share the `CoreDatasetTableField` table with dataset fields, differentiated by `chart_id`. Incorrect filtering could cross-contaminate. **Mitigation**: Always filter by `chart_id` in chart-specific queries; use `chart_id = 0` (or `None`) for dataset-level fields.

- **[Export endpoint completeness]** → `innerExportDataSetDetails` may require async worker integration that isn't fully ready. **Mitigation**: Start with synchronous data return; add async file generation in a follow-up change.

## Open Questions

- What is the exact response shape for `enumValueObj` vs `enumValue`? (Need to check Java backend or frontend consumption patterns during implementation)
- Does `getFieldTree` return a nested tree or a flat list with parent references? (Frontend code will clarify)
- Should `previewData` support the full union SQL (multi-table joins) or only single-table queries initially?
