## Capability: export-file-generation

Generates Excel files from export task data and serves them for download.

### Requirements

#### Requirement: Export tasks SHALL generate real .xlsx files
When the export worker processes a task with status `INITIATED`, it SHALL generate an `.xlsx` file using openpyxl and write it to the configured export directory.

##### Scenario: Task with data rows
- **WHEN** an export task has params containing `{"data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}`
- **THEN** the generated file SHALL contain two rows of data in a worksheet titled "Export"

##### Scenario: Task with no data
- **WHEN** an export task has empty or missing data in params
- **THEN** the generated file SHALL contain a single row with `["No data"]`

#### Requirement: Export files SHALL be stored in DE_EXPORT_DIR
Files SHALL be written to the directory specified by the `DE_EXPORT_DIR` environment variable, defaulting to `/tmp/de-exports`. The directory SHALL be created automatically if it doesn't exist.

##### Scenario: Custom export directory
- **WHEN** `DE_EXPORT_DIR=/data/exports` is set
- **THEN** export files SHALL be written to `/data/exports/`

#### Requirement: File metadata SHALL be updated on the task record
After successful file generation, the task record SHALL be updated with `file_name` (basename), `file_size` (bytes as float), and `file_size_unit` ("B").

##### Scenario: File generated successfully
- **WHEN** a 2048-byte file is generated as "report.xlsx"
- **THEN** the task record SHALL have `file_name="report.xlsx"`, `file_size=2048.0`, `file_size_unit="B"`

#### Requirement: Export task lifecycle SHALL follow INITIATED to SUCCESS/FAILED
Tasks transition through: `INITIATED` -> `RUNNING` -> `SUCCESS` or `FAILED`. Running tasks include a progress indicator.

##### Scenario: Successful export
- **WHEN** the export worker processes a task without errors
- **THEN** the task SHALL transition: `INITIATED` -> `RUNNING` (progress "10") -> `SUCCESS` (progress "100")

##### Scenario: Failed export
- **WHEN** file generation raises an exception after retries are exhausted
- **THEN** the task SHALL transition to `FAILED` with the error message stored in `msg`

#### Requirement: Download endpoint SHALL return FileResponse for completed exports
The `GET /de2api/exportCenter/download/{task_id}` endpoint SHALL return a `FileResponse` when the task is `SUCCESS` and the file exists on disk.

##### Scenario: Download a completed export
- **WHEN** a `GET` request is made for a task with status `SUCCESS` and the file exists
- **THEN** the response SHALL be a `FileResponse` with `application/octet-stream` media type

##### Scenario: Download a pending export
- **WHEN** a `GET` request is made for a task with status `RUNNING`
- **THEN** the response SHALL be a JSON object with `status` and `msg` fields indicating the file is not ready

##### Scenario: Download with missing file on disk
- **WHEN** a task has status `SUCCESS` but the file doesn't exist in the export directory
- **THEN** the response SHALL be a JSON object with `msg: "Export file not found"`

#### Requirement: File names SHALL be sanitized
Generated file names SHALL strip path components and append `.xlsx` if not already present.

##### Scenario: Task provides a plain name
- **WHEN** `file_name` is `"quarterly-report"`
- **THEN** the generated file SHALL be named `"quarterly-report.xlsx"`

##### Scenario: Task provides a name with path traversal
- **WHEN** `file_name` is `"../../etc/report.xlsx"`
- **THEN** the generated file SHALL be named `"report.xlsx"` (path stripped via `Path.name`)

#### Requirement: Failed export tasks SHALL be retryable
A task with status `FAILED` SHALL be reset to `INITIATED` and reprocessed by the retry mechanism.

##### Scenario: Retry a failed task
- **WHEN** `retry_task(task_id)` is called on a `FAILED` task
- **THEN** the task SHALL be reset to `INITIATED` with progress "0" and empty msg, then reprocessed
