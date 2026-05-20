## 1. Schemas

- [x] 1.1 Add new request/response schemas to `app/schemas/user.py`: `PersonEditRequest` (name?, email?, phone?), `UserSwitchLanguageRequest` (language), `UserBatchDeleteRequest` (ids: list[int]), `UserIpInfoResponse` (ip), `UserImportResponse` (success, failed)
- [x] 1.2 Add new request/response schemas to `app/schemas/role.py`: `RoleBeforeUnmountRequest` (roleId, userIds), `RoleBeforeUnmountInfoResponse` (id, name, account, remainingRoleCount), `RoleMountExternalRequest` (roleId, accounts), `RoleMountExternalResponse` (mounted, notFound)

## 2. User Profile & Session Endpoints

- [x] 2.1 Add `user_info` service method to `UserService` that returns current user's full detail (reuse `query_by_id` with `user.user_id`)
- [x] 2.2 Add `GET /user/info` route to user router
- [x] 2.3 Add `person_info` service method to `UserService` (same as user_info, returns current user detail)
- [x] 2.4 Add `GET /user/personInfo` route to user router
- [x] 2.5 Add `person_edit` service method to `UserService` that updates only name/email/phone on the current user
- [x] 2.6 Add `POST /user/personEdit` route to user router
- [x] 2.7 Add `switch_org` service method to `UserService` that validates org membership and returns a new token with updated oid
- [x] 2.8 Add `POST /user/switch/{id}` route to user router (needs `Request` param for token reissuance)
- [x] 2.9 Add `ip_info` route to user router that extracts client IP from request (X-Forwarded-For or client.host) — no service method needed, pure request-derived

## 3. User Preference Endpoints

- [x] 3.1 Add `switch_language` service method to `UserService` that updates language column and returns new token
- [x] 3.2 Add `POST /user/switchLanguage` route to user router
- [x] 3.3 Add `GET /user/personSysVariableInfo/{uid}` route to user router — returns empty dict `{}` (stub)

## 4. User Batch Operation Endpoints (Stubs)

- [x] 4.1 Add `batch_delete` service method to `UserService` that iterates user IDs and calls existing delete logic
- [x] 4.2 Add `POST /user/batchDel` route to user router
- [x] 4.3 Add `POST /user/batchImport` route to user router — stub accepting multipart file, returns `{"success": 0, "failed": 0}`
- [x] 4.4 Add `POST /user/excelTemplate` route to user router — stub returning empty Excel file as StreamingResponse
- [x] 4.5 Add `GET /user/errorRecord/{key}` route to user router — stub returning empty response
- [x] 4.6 Add `GET /user/clearErrorRecord/{key}` route to user router — stub returning success

## 5. Role Extra Endpoints

- [x] 5.1 Add `before_unmount_info` service method to `RoleService` that returns user details with remaining role counts
- [x] 5.2 Add `POST /role/beforeUnmountInfo` route to role router
- [x] 5.3 Add `mount_external_user` service method to `RoleService` that looks up users by account, mounts to role
- [x] 5.4 Add `POST /role/mountExternalUser` route to role router

## 6. Verification

- [ ] 6.1 Run `uv run ruff check .` from `core/pydataease-backend/` — must pass with no errors
- [ ] 6.2 Run `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` from `core/pydataease-backend/` — all tests pass
- [ ] 6.3 Verify import with `uv run python -c "from app.main import app; print(app.title)"` from `core/pydataease-backend/`
