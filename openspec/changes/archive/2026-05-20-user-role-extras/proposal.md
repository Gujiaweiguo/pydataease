## Why

The Python/FastAPI backend has core user and role CRUD endpoints working, but the frontend calls 14 additional endpoints that don't exist yet. These cover profile management, org switching, language preferences, batch user operations (import/export), and role external-user mounting. Without them, the frontend hits 404s on common user flows like viewing your own profile, switching organizations, or importing users from Excel.

## What Changes

- Add 5 user profile/session endpoints: `GET /user/info`, `POST /user/switch/{id}`, `GET /user/personInfo`, `POST /user/personEdit`, `GET /user/ipInfo`
- Add 2 user preference endpoints: `POST /user/switchLanguage`, `GET /user/personSysVariableInfo/{uid}`
- Add 5 user batch operation endpoints: `POST /user/batchDel`, `POST /user/batchImport`, `POST /user/excelTemplate`, `GET /user/errorRecord/{key}`, `GET /user/clearErrorRecord/{key}`
- Add 2 role extras endpoints: `POST /role/beforeUnmountInfo`, `POST /role/mountExternalUser`
- Batch import/export endpoints (`batchImport`, `excelTemplate`, `errorRecord`, `clearErrorRecord`) will ship as stubs that return success/empty responses, since full Excel parsing is a separate large feature
- `personSysVariableInfo` will return an empty dict since the sysVariable module doesn't exist yet

## Capabilities

### New Capabilities
- `user-profile-session`: User profile retrieval, personal info editing, organization switching, and IP info
- `user-preferences`: Language switching and system variable info retrieval
- `user-batch-operations`: Batch delete, batch import, Excel template download, and error record management
- `role-extras`: Pre-unmount info retrieval and external user mounting for roles

### Modified Capabilities
- `user-management`: Extends existing user management with profile and session endpoints that complement the auth/user CRUD already specified

## Impact

- **Routers**: `app/routers/user.py` (12 existing routes), `app/routers/role.py` (10 existing routes)
- **Services**: `app/services/user_service.py`, `app/services/role_service.py`
- **Models/DB**: No schema changes needed. All data lives in existing `core_user` and role tables.
- **API contract**: All endpoints under `/de2api` prefix, `X-DE-TOKEN` auth, `ResultMessage` response wrapper
- **Gate layer**: L0 (ruff) + L1 (pytest) for API/auth/repository changes. No database migrations, no Docker or frontend build needed.
