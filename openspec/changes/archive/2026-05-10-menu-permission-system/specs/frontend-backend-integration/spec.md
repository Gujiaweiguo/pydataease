## MODIFIED Requirements

### Requirement: Dev environment SHALL start PostgreSQL, FastAPI, and Vue frontend together
Updated to include the new `core_menu` table and additional bootstrap stubs.

#### Scenario: All services start and menu endpoint works
- **WHEN** the dev environment is running with fresh migrations
- **THEN** `GET /de2api/menu/query` with valid auth SHALL return the menu tree
