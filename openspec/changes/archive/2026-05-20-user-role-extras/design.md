## Context

The Python/FastAPI backend (`core/pydataease-backend/`) has 11 user routes and 10 role routes already working. The Vue frontend (`core/core-frontend/src/api/user.ts`) calls 14 additional endpoints that return 404. All endpoints follow the same 3-layer pattern: Router → Service → Repository, with `get_current_user` auth dependency and `get_user_service`/`get_role_service` DI factories.

Existing code conventions:
- Routers: `async def handler(payload, user: TokenUser = Depends(get_current_user), service: XService = Depends(get_x_service)) -> ReturnType`
- Services: `@final` class with `AsyncSession` constructor, repos as instance attrs
- Schemas: Pydantic v2 with `AliasChoices` for camelCase compat, `ConfigDict(populate_by_name=True, from_attributes=True)`
- IDs: `int` (BigInteger from `time.time_ns()`)
- Response wrapper: `ResultMessage` middleware wraps all responses as `{code, data, msg}`

## Goals / Non-Goals

**Goals:**
- Implement 14 missing API endpoints so the frontend stops hitting 404s
- Full implementation for profile/session/preferences/batch-delete endpoints that have clear data models
- Stub implementation for batch import/export endpoints (complex Excel parsing is out of scope)
- Follow existing code patterns exactly — no new architectural patterns

**Non-Goals:**
- Full Excel parsing/generation for `batchImport`, `excelTemplate`, `errorRecord` — these will return success/empty responses
- Building the `sysVariable` module — `personSysVariableInfo` returns empty dict
- Frontend changes — frontend already calls these endpoints
- Database migrations — all data lives in existing `core_user`/`core_role` tables

## Decisions

### D1: Profile endpoints reuse existing user query logic

`GET /user/info` and `GET /user/personInfo` both return user data. They'll use the existing `UserRepository` and the same `_build_user_items` / `query_by_id` patterns already in `UserService`. `user/info` returns the current user (from `user.user_id`), `personInfo` is identical (frontend uses both in different contexts).

### D2: Switch org updates the token's `oid`

`POST /user/switch/{id}` needs to verify the user belongs to the target org, then return a new token with the updated `oid`. The existing auth middleware (`TokenUser`) carries `oid` in the token. The service will validate org membership via the existing user-org relationship, then issue a new JWT via the existing token utility.

### D3: Switch language updates user's language field

`POST /user/switchLanguage` updates the `language` column on `core_user` and returns a new token with the updated language. The `TokenUser` schema already has a `language` field.

### D4: Person edit is self-service — restricted field set

`POST /user/personEdit` allows editing only `name`, `email`, `phone` on the calling user's own record. No `account`, `role_ids`, or `oid` changes. This is distinct from admin `user/edit`.

### D5: Batch delete reuses single-delete logic with iteration

`POST /user/batchDel` takes a list of user IDs and calls the existing delete logic for each. The existing `_ensure_not_last_admin` check applies per user.

### D6: Batch import/export are stubs

`POST /user/batchImport`, `POST /user/excelTemplate`, `GET /user/errorRecord/{key}`, `GET /user/clearErrorRecord/{key}` — all stub implementations. Import returns success with 0 records processed. Excel template returns an empty Excel file. Error record endpoints return empty/not-found. These can be fleshed out in a future change.

### D7: beforeUnmountInfo returns mount metadata

`POST /role/beforeUnmountInfo` takes a role ID and user IDs, returns info about what will be affected (which orgs, how many roles lost). Uses existing `RoleRepository` queries.

### D8: mountExternalUser mirrors mountUser

`POST /role/mountExternalUser` takes a role ID and external user identifiers (account-based lookup instead of internal user ID). Finds or creates the user reference, then reuses the existing `mount_user` logic.

### D9: IP info returns request metadata

`GET /user/ipInfo` extracts the client IP from the request (via `X-Forwarded-For` or `request.client.host`) and returns it with a timestamp. No database lookup needed — this is purely request-derived.

### D10: File download responses use StreamingResponse

For `excelTemplate` and `errorRecord` endpoints that return blobs, use `fastapi.responses.StreamingResponse` with `content_type="application/octet-stream"`. Even stubs follow this pattern for frontend compatibility.

## Risks / Trade-offs

- **[Stub endpoints return empty data]** → Frontend may show empty states or confusing UI for batch import. Mitigation: stubs return valid HTTP 200 with empty/zero values, frontend handles gracefully. Full implementation tracked as future work.
- **[Org switch reissues token]** → If token issuance has bugs, org switch could break sessions. Mitigation: reuse the exact same `create_token` utility used by login.
- **[mountExternalUser does account lookup]** → If external user accounts collide with internal ones, could mount wrong user. Mitigation: scope lookup by `origin` field (distinguish external vs internal users).
- **[No new DB migrations]** → All data fits existing schema. If `personEdit` needs fields not yet in `core_user`, we'd need a migration. Current model already has `name`, `email`, `phone`.

## Open Questions

- None. All endpoints have clear frontend contracts and existing code patterns to follow.
