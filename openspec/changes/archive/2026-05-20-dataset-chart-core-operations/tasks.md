## 1. Schemas and Request/Response Types

- [x] 1.1 Add `DatasetPreviewDataRequest` schema to `schemas/dataset.py` (dataset group ID, limit, offset, optional sort)
- [x] 1.2 Add `DatasetEnumValueRequest` schema to `schemas/dataset.py` (dataset group ID, field identifier, optional result limit)
- [x] 1.3 Add `DatasetEnumValueDsRequest` schema to `schemas/dataset.py` (datasource ID, table name, column name, result limit)
- [x] 1.4 Add `ChartFieldEnumRequest` schema to `schemas/chart.py` (field ID, field type, optional chart ID / filter context)
- [x] 1.5 Add `ChartDrillRequest` schema to `schemas/chart.py` (field ID, chart ID, drill path / dimension context)
- [x] 1.6 Add `DatasetExportRequest` schema to `schemas/chart.py` (chart ID or dataset group ID + view config)

## 2. Repository Layer

- [x] 2.1 Add `list_by_chart` method to `DatasetFieldRepository` — query fields filtered by `chart_id`
- [x] 2.2 Add `copy_field_to_chart` method to `DatasetFieldRepository` — duplicate a field record with new ID and target `chart_id`
- [x] 2.3 Add `delete_chart_field` method to `DatasetFieldRepository` — delete a single field by ID, verifying it has a `chart_id`
- [x] 2.4 Add `delete_all_chart_fields` method to `DatasetFieldRepository` — delete all fields matching a `chart_id`
- [x] 2.5 Add `get_field_tree_by_group` method to `DatasetFieldRepository` — retrieve fields grouped by `group_type` for tree structure

## 3. Service Layer — Dataset Data Operations

- [x] 3.1 Add `preview_data(request)` to `DatasetService` — resolve dataset group base SQL, execute with pagination, return rows + field metadata
- [x] 3.2 Add `get_enum_values(request)` to `DatasetService` — build `SELECT DISTINCT` for a field, execute against datasource, return flat value list
- [x] 3.3 Add `get_enum_value_objects(request)` to `DatasetService` — same as `get_enum_values` but return `{text, value}` object pairs
- [x] 3.4 Add `get_enum_values_from_datasource(request)` to `DatasetService` — connect to datasource directly, query distinct values for a table/column
- [x] 3.5 Add `get_field_tree(group_id)` to `DatasetService` — retrieve fields and organize into dimension/quota tree structure
- [x] 3.6 Add `inner_export_dataset_details(request)` to `ChartService` — resolve chart dataset, execute full query, return for export

## 4. Service Layer — Chart Field Operations

- [x] 4.1 Add `list_fields_by_dq(dataset_group_id, chart_id)` to `ChartService` — retrieve fields for a dataset, organized by dimension/quota, considering chart-level custom fields
- [x] 4.2 Add `copy_field(field_id, chart_id)` to `ChartService` — duplicate a field as a chart custom field with new ID
- [x] 4.3 Add `delete_chart_field(field_id)` to `ChartService` — delete a chart custom field with validation
- [x] 4.4 Add `delete_all_chart_fields(chart_id)` to `ChartService` — delete all custom fields for a chart

## 5. Service Layer — Chart Data Enumeration

- [x] 5.1 Add `get_field_enum_data(field_id, field_type, request)` to `ChartService` — resolve field's dataset, build distinct-values query with chart filters, execute
- [x] 5.2 Add `get_drill_field_data(field_id, request)` to `ChartService` — build drill-down query with current dimension context, execute
- [x] 5.3 Add `check_same_dataset(view_id_source, view_id_target)` to `ChartService` — compare `table_id` of two charts, return boolean

## 6. Router Layer — Dataset Data Endpoints

- [x] 6.1 Add `POST /datasetData/previewData` route to `dataset.py` router with `use` permission
- [x] 6.2 Add `POST /datasetData/enumValue` route to `dataset.py` router with `use` permission
- [x] 6.3 Add `POST /datasetData/enumValueObj` route to `dataset.py` router with `use` permission
- [x] 6.4 Add `POST /datasetData/enumValueDs` route to `dataset.py` router with `use` permission
- [x] 6.5 Add `POST /datasetData/getFieldTree` route to `dataset.py` router with `use` permission
- [x] 6.6 Add `POST /datasetData/innerExportDataSetDetails` route to `dataset.py` router with `use` permission

## 7. Router Layer — Chart Field Endpoints

- [x] 7.1 Add `POST /chart/listByDQ/{id}/{chartId}` route to `chart.py` router with auth
- [x] 7.2 Add `POST /chart/copyField/{id}/{chartId}` route to `chart.py` router with auth
- [x] 7.3 Add `POST /chart/deleteField/{id}` route to `chart.py` router with auth
- [x] 7.4 Add `POST /chart/deleteFieldByChart/{chartId}` route to `chart.py` router with auth

## 8. Router Layer — Chart Data Endpoints

- [x] 8.1 Add `POST /chartData/getFieldData/{fieldId}/{fieldType}` route to `chart.py` router with auth
- [x] 8.2 Add `POST /chartData/getDrillFieldData/{fieldId}` route to `chart.py` router with auth
- [x] 8.3 Add `GET /chart/checkSameDataSet/{viewIdSource}/{viewIdTarget}` route to `chart.py` router with auth

## 9. Verification

- [x] 9.1 Run `uv run ruff check .` from `core/pydataease-backend/` — zero errors
- [x] 9.2 Run `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` from `core/pydataease-backend/` — all tests pass (new tests 22/22 pass; pre-existing unrelated test failures noted)
- [x] 9.3 Run `uv run python -c "from app.main import app; print(app.title)"` from `core/pydataease-backend/` — import succeeds without errors
