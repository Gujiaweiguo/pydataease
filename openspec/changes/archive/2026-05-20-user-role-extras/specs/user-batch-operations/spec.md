## ADDED Requirements

### Requirement: Batch user deletion
The backend SHALL provide a `POST /user/batchDel` endpoint that deletes multiple users by their IDs. The backend SHALL apply the same safeguards as single-user deletion (e.g., preventing deletion of the last admin).

#### Scenario: Admin batch deletes multiple users
- **WHEN** an authenticated admin sends `POST /user/batchDel` with `{"ids": [id1, id2, id3]}`
- **THEN** the backend SHALL delete each user that passes the deletion safeguards and return a success response

#### Scenario: Batch delete includes last admin
- **WHEN** an authenticated admin sends `POST /user/batchDel` with IDs that include the last remaining admin user
- **THEN** the backend SHALL skip deletion of that admin user and delete the others, returning success

#### Scenario: Empty ID list
- **WHEN** an authenticated admin sends `POST /user/batchDel` with `{"ids": []}`
- **THEN** the backend SHALL return success without performing any deletions

### Requirement: Batch user import (stub)
The backend SHALL provide a `POST /user/batchImport` endpoint that accepts a multipart file upload. In this initial implementation, the endpoint SHALL accept the upload and return a stub success response indicating 0 records processed.

#### Scenario: User uploads an import file
- **WHEN** an authenticated admin sends `POST /user/batchImport` with a multipart file
- **THEN** the backend SHALL accept the file and return a response with `{"success": 0, "failed": 0}` indicating no records were processed. Full Excel parsing will be implemented in a future change.

### Requirement: Excel template download (stub)
The backend SHALL provide a `POST /user/excelTemplate` endpoint that returns a downloadable Excel template file. In this initial implementation, the endpoint SHALL return an empty Excel file with appropriate headers.

#### Scenario: User downloads import template
- **WHEN** an authenticated admin sends `POST /user/excelTemplate`
- **THEN** the backend SHALL return a file download response with `Content-Type: application/octet-stream` and `Content-Disposition: attachment` header. The file SHALL be a valid but empty Excel template.

### Requirement: Error record download (stub)
The backend SHALL provide a `GET /user/errorRecord/{key}` endpoint that returns error records from a previous import. In this initial implementation, the endpoint SHALL return a 404 or empty response since no imports generate errors yet.

#### Scenario: User requests error records with a key
- **WHEN** an authenticated admin sends `GET /user/errorRecord/{key}`
- **THEN** the backend SHALL return an empty response or 404, since the stub import does not generate error records

### Requirement: Error record clearing (stub)
The backend SHALL provide a `GET /user/clearErrorRecord/{key}` endpoint that clears error records from a previous import. In this initial implementation, the endpoint SHALL return success immediately.

#### Scenario: User clears error records
- **WHEN** an authenticated admin sends `GET /user/clearErrorRecord/{key}`
- **THEN** the backend SHALL return a success response immediately
