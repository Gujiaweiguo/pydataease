# Bugs Found During Testing Audit

> **Audit Date**: 2026-05-18
> **Test Count**: 945 tests across 72 test files
> **Coverage Audited**: 85% on services
> **Methodology**: Systematic review of test files for suspicious patterns (weakened assertions, silent exceptions, fail-open tests), cross-referenced with source code to confirm bugs.

---

## Critical

### BUG-001: Missing Permission Checks on 13 Destructive Dataset Endpoints

- **File**: `app/routers/dataset.py`, lines 52-167
- **Description**: Of the 16 dataset endpoints, only 3 (`tree`, `create`, `save`) call `perm.require_resource_access()`. The remaining 13 endpoints — including **delete**, **perDelete** (permanent delete), **rename**, **move**, **exportDataset**, **previewSql**, **details**, **barInfo**, **get**, **dsDetails**, **detailWithPerm**, **tableField**, **getDatasetTotal** — have zero permission enforcement. Any authenticated user can rename, move, permanently delete, or export any dataset.
- **Impact**: Any authenticated user can perform destructive operations on any dataset regardless of their role or permissions. This is a complete authorization bypass for the dataset module.
- **Evidence**: Tests in `test_dataset_permission.py` lines 296-351 explicitly document this with test names like `test_dataset_rename_still_works_without_permission_check` and assert 200 status even when `DenyAllPermissionService` is active.
- **Fix**: Add `perm: PermissionService = Depends(get_permission_service)` and `await perm.require_resource_access(user, "dataset", "manage")` to `rename`, `move`, `delete`, `perDelete`, `exportDataset`. Add `"use"` level checks to read endpoints.

---

### BUG-002: SQL Injection via String Formatting in `preview_data`

- **File**: `app/services/datasource_service.py`, lines 401-403
- **Description**: `preview_data` constructs SQL queries via f-string formatting with user-controlled `table_name`:
  ```python
  rows = await connection.fetch(
      f'SELECT * FROM "{schema}"."{table_name}" LIMIT 10'
      if canonical_type(datasource.type) == "postgresql"
      else f"SELECT * FROM `{table_name}` LIMIT 10"
  )
  ```
  `table_name` comes directly from `payload.get("table") or payload.get("tableName")`. While `asyncpg.fetch()` rejects multi-statement injection, the identifier quoting is breakable. For MySQL, backtick breakout produces malformed SQL. Error messages leak the full query structure including injected text.
- **Impact**: SQL syntax manipulation enables error-based information disclosure about database structure. In MySQL configurations with multi-statement enabled, full SQL injection is possible.
- **Evidence**: Compare with `get_fields` at lines 232-243 which correctly uses parameterized queries (`$1`, `$2`). The test `test_sql_security.py` tests for basic injection but doesn't test identifier breakout patterns.
- **Fix**: Validate `table_name` against allowlist (`[a-zA-Z0-9_]`), or properly escape quotes/backticks. Ideally use parameterized queries where possible:
  ```python
  safe_table = table_name.replace('"', '""')
  rows = await connection.fetch(f'SELECT * FROM "{safe_schema}"."{safe_table}" LIMIT 10')
  ```

---

### BUG-003: SQL Injection via `apply_row_filters` — Subquery and UNION Bypass

- **File**: `app/services/data_permission_service.py`, lines 24-47
- **Description**: `apply_row_filters` uses naive regex (`_WHERE_RE = re.compile(r"\bWHERE\b", re.IGNORECASE)`) to find WHERE clauses and injects `filter_sql` fragments via string concatenation. Two critical problems:
  1. **Subquery mismatch**: regex matches the *first* `WHERE` in the SQL. For `SELECT * FROM (SELECT * FROM t WHERE x=1) sub`, the filter is appended to the inner WHERE, not the outer query — permission filter applied at wrong scope.
  2. **UNION queries**: For `SELECT * FROM a UNION SELECT * FROM b`, appending `AND (filter)` only filters the second branch, allowing full data bypass for the first.
- **Impact**: Row-level permission filters can be completely bypassed using subqueries or UNION constructs, giving users access to data they should not see.
- **Evidence**: Tests in `test_data_permission_service_coverage.py` only test simple SELECT statements, never subqueries or UNIONs.
- **Fix**: Wrap the user's query in an outer SELECT: `SELECT * FROM ({original_sql}) _perm_filtered WHERE {filters}`. This avoids all subquery and UNION issues.

---

### BUG-004: Share Link Token Issued Regardless of Auth Status (Ticket/Password/Expiry)

- **File**: `app/services/share_service.py`, lines 49-121
- **Description**: In `proxy_info()`, ticket validation (lines 80-98) and password validation (lines 62-77) produce purely informational fields in the response body. A valid JWT link token is **always** generated and returned via the `x-de-link-token` header (line 107), even when the password is wrong (`pwd_valid=False`), the ticket is invalid (`ticket_valid=False`), or the share is expired. For wrong-password and invalid-ticket cases, the link token has a full 24-hour validity window and is fully usable.
- **Impact**: Any client calling `/share/proxyInfo` receives a valid link token that grants resource access, regardless of whether they provided correct credentials. Complete authentication bypass for share-protected resources.
- **Evidence**: No test verifies that the `x-de-link-token` header is absent when auth fails. Tests only check response body fields.
- **Fix**: Move link token generation inside a gate — only generate after successful password, ticket, and expiry validation:
  ```python
  if is_expired or (share.pwd and not pwd_valid) or (share.ticket_require and not ticket_vo.ticket_valid):
      return response  # no link token
  link_token = self._generate_link_token(share, current_ms)
  ```

---

### BUG-005: Cross-Share Ticket Reuse — Ticket Not Validated Against Share UUID

- **File**: `app/services/share_service.py`, lines 81-98
- **Description**: When `payload.ticket` is provided, the code looks up the ticket by ticket string only (`ticket_repo.get_by_ticket(payload.ticket)`). It never checks that `ticket_record.uuid == share.uuid`. A ticket from Share A can be used to access Share B.
- **Impact**: A single valid ticket grants access to ALL shares in the system, not just the one it was issued for.
- **Evidence**: No test creates a ticket for Share A and attempts to use it on Share B.
- **Fix**: Add UUID cross-check:
  ```python
  elif ticket_record.uuid != share.uuid:
      ticket_vo = TicketValidVO(ticket_valid=False, ticket_exp=False)
  ```

---

### BUG-006: SSRF via `load_remote_file` — No URL Scheme Validation

- **File**: `app/services/datasource_service.py`, lines 501-521
- **Description**: `load_remote_file` accepts arbitrary URLs with no scheme validation. `follow_redirects=True` compounds the issue. An attacker can supply:
  - `http://169.254.169.254/latest/meta-data/` — AWS instance metadata
  - `http://localhost:5432/` — internal service probing
  - `file:///etc/passwd` — local file read
- **Impact**: Full Server-Side Request Forgery — access to cloud metadata, internal services, and local files.
- **Evidence**: No test validates URL schemes; all tests use valid HTTP URLs.
- **Fix**: Validate URL scheme to HTTP/HTTPS only, optionally block private IP ranges:
  ```python
  parsed = urlparse(url)
  if parsed.scheme not in ("http", "https"):
      raise HTTPException(status_code=400, detail="Only HTTP/HTTPS URLs supported")
  ```

---

## High

### BUG-007: No Permission Rules = No Access Control (Fail-Open)

- **File**: `app/services/data_permission_service.py`, lines 63-94 (`collect_row_filters`)
- **Description**: When a non-admin, non-whitelisted user has no row permission rules at any level, the method returns an empty list. In `sql_executor.py` line 131, `if row_filters:` means empty list = no WHERE clause = user sees **all rows**. Any newly created user has unrestricted data access until an admin explicitly creates permission rules.
- **Impact**: New users, or users assigned to new datasets, see all data by default. Fail-open design for row-level security.
- **Fix**: Add a configuration option for default-deny. When no rules exist for a non-admin user, return `"1=0"` (deny all rows) or at minimum log a warning.

---

### BUG-008: Fail-Open When No Permission Point Exists

- **File**: `app/services/permission_service.py`, lines 113-122 (`has_resource_permission`)
- **Description**: If no `CorePermissionPoint` row exists for a given `resource_type + permission_type` combination, the method returns `True`. If an admin forgets to create a permission point for a new resource type, everyone gets access.
- **Impact**: Any resource without an explicitly defined permission point is accessible to all users.
- **Evidence**: `test_dataset_permission.py` line 146-154 explicitly tests and validates this fail-open behavior.
- **Fix**: Invert the default — if no permission point exists, return `False`. Add a config flag for backward compatibility.

---

### BUG-009: TOCTOU Race Condition Between Permission Check and Query Execution

- **File**: `app/services/sql_executor.py`, lines 112-157 (`_execute_with_permissions`)
- **Description**: Permission check (row filters collected at line 130) and query execution (line 137) happen in separate sessions/connections. Between them, permission rules could be revoked or modified. Column rules are checked in a third session (lines 153-155) after query execution.
- **Impact**: Users may access data based on stale permission snapshots. Revoked permissions don't take effect until the next request.
- **Fix**: Perform all permission checks and query execution within the same database transaction.

---

### BUG-010: `resolve()` Never Enforces `ticket_require` — Ticket Requirement Bypass

- **File**: `app/services/share_service.py`, lines 213-233; `app/routers/share.py`, lines 147-157
- **Description**: `resolve()` checks share existence, expiration, and password, but never checks `share.ticket_require`. The router at `/share/view/{uuid}` accepts a `ticket` query parameter but discards it. Shares with `ticket_require=True` can be accessed without a ticket via the public view endpoint.
- **Impact**: Ticket requirement on shares is completely bypassed via `/share/view/{uuid}`.
- **Evidence**: No test creates a share with `ticket_require=True` and verifies rejection without a ticket.
- **Fix**: Add ticket validation to `resolve()` and update the router to pass `ticket` to the method.

---

### BUG-011: `save()` Allows Duplicate Share UUIDs Across Different Resources

- **File**: `app/services/share_service.py`, line 163
- **Description**: When creating a new share with a user-provided UUID, there is no uniqueness check. `edit_uuid()` has this check but `save()` does not. No database-level unique constraint on `uuid`.
- **Impact**: UUID collision can cause one share to overwrite another's access, or cause unpredictable behavior in share resolution.
- **Fix**: Add uniqueness check before creation, and add a database unique constraint on `uuid`.

---

### BUG-012: `generate_temp_ticket()` Uses `random.choices` Instead of Cryptographically Secure `secrets`

- **File**: `app/services/share_service.py`, lines 431-436
- **Description**: Temporary tickets are generated using `random.choices` (Mersenne Twister PRNG, predictable). Security tokens must use the `secrets` module.
- **Impact**: Predictable ticket tokens can be brute-forced, bypassing ticket-based access controls.
- **Fix**: Replace `random.choices` with `secrets.choice`:
  ```python
  import secrets
  return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
  ```

---

### BUG-013: `ShareResponse` Leaks Plaintext Password in API Responses

- **File**: `app/schemas/share.py`, line 64; `app/services/share_service.py` (multiple methods)
- **Description**: `ShareResponse` includes `pwd: str | None = None`. Every endpoint returning `ShareResponse` — including the public `/share/view/{uuid}` — exposes the plaintext password.
- **Impact**: Share passwords visible through API responses, enabling unauthorized access if response is intercepted.
- **Fix**: Remove `pwd` from `ShareResponse` for public-facing endpoints. Add a `has_pwd: bool` field. Use separate response schemas for admin vs public endpoints.

---

### BUG-014: Default `secret_key` == `share_secret_key` Enables Cross-Token-Type Confusion

- **File**: `app/settings/config.py`, lines 14-15
- **Description**: Both default to `"change-me-in-production"`. A link token (signed with `share_secret_key`) is also valid when verified with `secret_key`, and vice versa. Combined with the middleware's embedded token fallthrough (`auth.py` line 100: `token = de_token or embedded_token`), a share token can be treated as a user token.
- **Impact**: If either secret is compromised, an attacker can forge both user tokens and share tokens. Cross-type token confusion possible in default deployments.
- **Fix**: Generate unique defaults or require both to be set independently. Add startup validation that `secret_key != share_secret_key`.

---

### BUG-015: Global `secret_key` Fallback Survives Password Changes

- **File**: `app/middleware/auth.py`, lines 127-132
- **Description**: In `_decode_user_token`, if the password-derived JWT secret fails, the code falls back to the global `secret_key`. Legacy tokens signed with the global key survive password changes — changing a user's password does NOT invalidate such tokens.
- **Impact**: An attacker who stole a legacy token retains access even after the user changes their password.
- **Fix**: Remove the global fallback, or add a `password_changed_at` timestamp and reject tokens issued before it.

---

### BUG-016: Token Refresh Has No Maximum Lifetime Window

- **File**: `app/routers/login.py`, line 60
- **Description**: `/login/refresh` uses `options={"verify_exp": False}` with no `iat` check or max-refresh-window. A token stolen at any point can be refreshed perpetually (until the user changes their password).
- **Impact**: Compromised tokens never expire through refresh — indefinite access persistence for attackers.
- **Fix**: Add a maximum refresh window (e.g., 7 days). Check `iat` from claims and reject tokens older than the window.

---

### BUG-017: Connection Error Messages Leak Sensitive Infrastructure Details

- **File**: `app/services/datasource_service.py`, lines 470, 483
- **Description**: Both `_validate_connection` and `_open_connection` format exception details directly into HTTP responses: `raise HTTPException(status_code=400, detail=f"Connection failed: {exc}")`. Database connection errors from asyncpg/asyncmy include hostnames, ports, database names, and sometimes stack traces.
- **Impact**: Information leakage of internal infrastructure (hostnames, ports, database names) to any user who can trigger a connection test.
- **Fix**: Log the full error server-side, return generic message to client:
  ```python
  logger.warning("Datasource connection failed: %s", exc)
  raise HTTPException(status_code=400, detail="Unable to connect to datasource. Please verify configuration.")
  ```

---

### BUG-018: No File Size Limit on Upload — OOM Vector

- **File**: `app/services/datasource_service.py`, lines 496-499
- **Description**: `upload_file` reads entire file into memory via `file.read()` with no size check. The file is then parsed by openpyxl (inflating in-memory representation), base64-encoded (33% expansion), and later stored in database JSONB.
- **Impact**: A malicious large file (e.g., 500MB Excel) can exhaust server memory (2GB+ with openpyxl inflation), causing denial of service.
- **Fix**: Add a size check before reading:
  ```python
  MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
  content = await file.read()
  if len(content) > MAX_UPLOAD_SIZE:
      raise HTTPException(status_code=413, detail="File size exceeds 50MB limit")
  ```

---

### BUG-019: Entire Uploaded File Stored as Base64 in Database Configuration

- **File**: `app/services/datasource_service.py`, lines 534-537
- **Description**: Full raw file content is base64-encoded and attached to every sheet object in the configuration: `_raw = base64.b64encode(content).decode()`. When saved, the entire file content (+ 33% base64 overhead) is stored in `CoreDatasource.configuration` JSONB column. The base64 is duplicated per sheet.
- **Impact**: Database bloat — a 10MB Excel file with 3 sheets stores ~40MB of JSONB data per datasource row. No cleanup mechanism exists.
- **Fix**: Store file content in object storage (filesystem, S3) and keep only a reference. At minimum, store base64 once (not per-sheet).

---

## Medium

### BUG-020: `_mask_passwords` Ignores Passwords Inside Lists

- **File**: `app/services/datasource_service.py`, lines 805-810
- **Description**: `_mask_passwords` recurses into nested dicts but not into lists. If configuration contains a list of dicts with password fields (e.g., API datasource items), those passwords are not masked.
- **Impact**: Passwords in API datasource configurations may be exposed via `/hidePw` endpoint.
- **Fix**: Add list handling:
  ```python
  elif isinstance(config[key], list):
      for item in config[key]:
          if isinstance(item, dict):
              _mask_passwords(item)
  ```

---

### BUG-021: `_parse_excel_sheets` Silently Drops Data for Duplicate Column Headers

- **File**: `app/services/datasource_service.py`, line 547
- **Description**: Uses `dict(zip(headers, row))` which silently keeps only the last value for duplicate column names. Data from earlier same-named columns is lost with no warning.
- **Impact**: Silent data loss when Excel sheets have duplicate column headers.
- **Fix**: Detect duplicate headers and append a suffix (e.g., `amount_1`, `amount_2`).

---

### BUG-022: CSV Parsing Fails with Non-UTF-8 Encoding

- **File**: `app/services/datasource_service.py`, line 567
- **Description**: `content.decode("utf-8-sig")` raises `UnicodeDecodeError` for non-UTF-8 files (Latin-1, GBK, Shift-JIS), propagating as a 500 error.
- **Impact**: Users with non-UTF-8 CSV files get unhelpful 500 errors instead of proper error messages.
- **Fix**: Try multiple encodings or use `chardet` for detection.

---

### BUG-023: Silent Org Reassignment Hides Privilege Changes

- **File**: `app/middleware/auth.py`, lines 176-186
- **Description**: When a user's token contains an `oid` they're no longer a member of, `_validate_org_membership` silently reassigns them to `user_orgs[0].id` instead of rejecting the request. The result is non-deterministic for multi-org users.
- **Impact**: Users removed from an org silently get reassigned to another org without notification, potentially accessing data in an unintended org.
- **Fix**: Return a 401 indicating the org membership is invalid, forcing re-authentication.

---

### BUG-024: Link Token Path Skips User Existence/Enabled Check — Accessible on All Routes

- **File**: `app/middleware/auth.py`, lines 69-75, 163-172
- **Description**: A valid link token creates a `TokenUser` without checking if the referenced user exists or is enabled. The resulting `TokenUser` passes through to any protected route (not just share-viewing). Routes using `get_optional_user` or directly reading `request.state.user` accept it.
- **Impact**: If `share_secret_key` is leaked, attackers can forge link tokens with arbitrary `uid` (including admin `uid=1`) to impersonate any user.
- **Fix**: Add user existence/enabled validation for link tokens, or restrict link tokens to share-specific routes.

---

### BUG-025: Non-Deterministic Same-Priority Column Rule Resolution

- **File**: `app/services/data_permission_service.py`, lines 128-133
- **Description**: When multiple rules exist at the same priority level (e.g., two role-level rules for the same field), the code uses `>=` comparison meaning the last-processed rule wins. Since `_fetch_column_rules` has no explicit `ORDER BY`, the winning rule is non-deterministic.
- **Impact**: Users with multiple role-level column rules may get inconsistent masking/disabling behavior across requests.
- **Fix**: Define a deterministic tiebreaker — always use the most restrictive action (`disable > desensitize > mask`), or add an explicit ordering column.

---

### BUG-026: Race Condition in `save()` — TOCTOU on Resource Uniqueness

- **File**: `app/services/share_service.py`, lines 143-176
- **Description**: `save()` checks `get_by_resource_id()`, then creates/updates. Between check and create, a concurrent request could create a duplicate share for the same resource. No database-level unique constraint on `resource_id`.
- **Impact**: Concurrent requests can create duplicate shares for the same resource.
- **Fix**: Add unique constraint on `resource_id` or use `INSERT ... ON CONFLICT` upsert.

---

### BUG-027: Race Condition in `edit_uuid()` — TOCTOU on UUID Uniqueness

- **File**: `app/services/share_service.py`, lines 405-416
- **Description**: Checks UUID uniqueness, then updates. Between check and update, another request could claim the same UUID. No row-level locking.
- **Impact**: UUID collision under concurrent requests.
- **Fix**: Add database unique constraint on `uuid` and handle `IntegrityError`.

---

### BUG-028: Admin Bypass Hardcoded to `user_id == 1`

- **File**: `app/services/data_permission_service.py` (lines 69, 112), `app/services/permission_service.py` (lines 109, 175), `app/services/row_permission_service.py` (multiple lines), `app/middleware/auth.py` (line 179)
- **Description**: Every admin check uses `user.user_id == 1` as a hardcoded magic number. `TokenUser` has no `role` or `is_admin` field. If admin user_id changes or multiple admins are needed, every check must be found and updated.
- **Impact**: Brittle admin identification. If uid=1 is deleted and recreated as non-admin, they retain god-mode. No support for multiple admins.
- **Fix**: Add `is_admin: bool = False` to `TokenUser`, populate from JWT claims or user lookup, replace all `user_id == 1` checks.

---

### BUG-029: `load_remote_file` Has No Response Content-Type/Size Validation

- **File**: `app/services/datasource_service.py`, lines 515-521
- **Description**: Downloads any URL response into memory without checking content-length or content-type. A 5GB video response will be fully downloaded before parsing fails.
- **Impact**: Memory exhaustion via large remote file downloads.
- **Fix**: Check `Content-Length` header before downloading, and validate content-type.

---

### BUG-030: `_excel_table_name` Can Exceed PostgreSQL 63-Char Identifier Limit

- **File**: `app/services/datasource_service.py`, lines 666-668
- **Description**: No length limit on the generated table name. Long CSV filenames produce table names exceeding PostgreSQL's 63-char identifier limit.
- **Impact**: SQL errors when creating tables for Excel/CSV datasources with long names.
- **Fix**: Truncate the safe portion to ensure total is within limits:
  ```python
  max_safe = 63 - 6 - 1 - 10  # 46 chars for "excel_" + "_" + hash(10)
  safe = safe[:max_safe]
  ```

---

### BUG-031: `_excel_sheets` Casts List Items Without Runtime Validation

- **File**: `app/services/datasource_service.py`, lines 619-626
- **Description**: Uses `cast()` (type-checker hint, not runtime check) on configuration list items. If items are non-dict, downstream `.get()` calls raise `AttributeError`.
- **Impact**: Unhandled 500 errors for malformed configuration data.
- **Fix**: Filter list items with runtime check: `return [item for item in configuration if isinstance(item, dict)]`.

---

### BUG-032: Tests Codify Missing Permission Enforcement as Expected Behavior

- **File**: `tests/test_dataset_permission.py`, lines 296-351
- **Description**: Four test methods assert that destructive dataset operations succeed without permission checks. Test names include "still_works_without_permission_check", documenting a security vulnerability as expected behavior rather than flagging it as a bug.
- **Impact**: Critical security gap (BUG-001) appears to pass CI because tests greenlight it.
- **Fix**: Mark tests with `@pytest.mark.xfail(reason="BUG-001: Missing permission check")` until the router is fixed, then update to assert 403.

---

## Low

### BUG-033: No Rate Limiting on `/login/refresh`

- **File**: `app/routers/login.py`, line 32
- **Description**: `/login/localLogin` has `@limiter.limit("5/minute")` but `/login/refresh` has no rate limiting. Allows brute-force token guessing and is a minor DoS vector.
- **Fix**: Add `@limiter.limit("20/minute")` to the refresh endpoint.

---

### BUG-034: Double User DB Lookup on Every Authenticated Request

- **File**: `app/middleware/auth.py` line 123 + `app/dependencies/auth.py` line 21
- **Description**: The middleware loads the user from DB, then `get_current_user` dependency loads the same user again. Every authenticated request performs 2 database lookups for the same user record.
- **Impact**: Performance overhead — approximately 2x unnecessary DB load per authenticated request.
- **Fix**: Cache the loaded user in `request.state` during middleware and reuse in the dependency.

---

### BUG-035: MD5 Used for JWT Secret Derivation

- **File**: `app/utils/password_utils.py`, line 48
- **Description**: `derive_jwt_secret` uses `hashlib.md5(password_hash.encode("utf-8")).hexdigest()`. MD5 is cryptographically broken. While the input (bcrypt hash) has high entropy, this fails strict security audits.
- **Impact**: Theoretical weakness in JWT secret derivation. Practical impact limited by high-entropy input.
- **Fix**: For new deployments, use HMAC-SHA256 with a pepper. Keep MD5 only for backward compatibility with existing tokens.

---

### BUG-036: `record_access()` Silently Swallows All Exceptions

- **File**: `app/services/share_service.py`, lines 274-286
- **Description**: `except Exception` catches everything and only logs. Access counting can silently fail forever, and a broken session can corrupt the caller's transaction.
- **Impact**: Silent failure in access tracking; potential transaction corruption.
- **Fix**: Use a separate database session/savepoint for access recording to isolate failures.

---

### BUG-037: `enable_ticket()` Unsafe `int()` Conversion

- **File**: `app/services/share_service.py`, line 427
- **Description**: `int(resource_id)` called on a `str` parameter without error handling. Non-numeric `resource_id` causes unhandled `ValueError` → 500 error.
- **Fix**: Change schema to `resource_id: int` or wrap with try/except.

---

### BUG-038: `_mask_value` Produces Misleading Results for Empty/Single-Char Values

- **File**: `app/services/data_permission_service.py`, lines 50-54
- **Description**: Empty string `""` returns `"*"`, and single character `"a"` also returns `"*"`. Masked empty strings look identical to masked single characters. Numeric values like `42` become `"4*"` which may be surprising.
- **Fix**: Return `""` for empty strings. Document non-string value handling.

---

### BUG-039: Integration Permission Tests Always Skipped in Normal CI

- **File**: `tests/test_data_permission_service_coverage.py`, lines 338-340
- **Description**: All integration tests for the permission service are gated by `DE_E2E=1` and skipped by default. The critical permission-enforcement logic (database queries for whitelist, rule lookups) is only tested in skipped tests.
- **Impact**: Permission regressions may go undetected in normal CI.
- **Fix**: Ensure CI runs `DE_E2E=1` for permission tests on every PR that touches permission code.

---

### BUG-040: Test Fake `validate_by_id` Diverges from Real Service Contract

- **File**: `tests/test_datasource_advanced.py`, lines 95-96
- **Description**: Fake returns `{"status": "Success"}` (1 key) but real service returns `{"status": ..., "type": ...}` (2 keys). Test asserts exact match with the fake. If real service were used, the test would fail.
- **Impact**: Contract mismatch masked by inaccurate test fake.
- **Fix**: Update fake to return both keys: `{"status": "Success", "type": "pg"}`.

---

### BUG-041: Test `test_get_datasource` Asserts Password IS Returned in Plaintext

- **File**: `tests/test_datasource_advanced.py`, line 236
- **Description**: `assert data["configuration"]["password"] == "secret123"` confirms `/get/{id}` returns plaintext passwords. No corresponding test verifies the frontend uses `/hidePw/{id}` in read-only contexts.
- **Impact**: Documents password exposure as expected behavior without verifying safe usage.
- **Fix**: Add test documenting when `/get/` is appropriate vs `/hidePw/`, and verify frontend contract.

---

### BUG-042: Test Conftest `is_member` Too Simplistic for Multi-Org

- **File**: `tests/conftest.py`, lines 73-75
- **Description**: Fake `is_member` only returns `True` for the user's current `oid`. In production, users can belong to multiple orgs. Tests may pass with fake but fail in production.
- **Impact**: Multi-org edge cases not caught by test suite.
- **Fix**: Update conftest fake to support multi-org membership.

---

### BUG-043: `_download_remote_file` Filename Extraction is Fragile

- **File**: `app/services/datasource_service.py`, line 520
- **Description**: `filename = url.rstrip("/").split("/")[-1]` fails for URLs with query parameters. Should check `Content-Disposition` header first.
- **Impact**: Incorrect filename detection for remote file downloads, potentially breaking file type detection.
- **Fix**: Parse `Content-Disposition` header first, fall back to URL path extraction.

---

## Critical (Additional Findings)

### BUG-044: Internal Database Data Exfiltration via Dataset SQL Preview

- **File**: `app/services/dataset_service.py`, lines 306-347; `app/routers/dataset.py`, line 167
- **Description**: When `POST /datasetData/previewSql` is called with no `datasourceId`, the code falls through to `self.sql_executor.execute_select(sql)` which executes user-supplied SQL against the **internal metadata PostgreSQL database** — the same one holding `core_user` (password hashes), `core_datasource` (external DB credentials), and all other internal tables. `validate_readonly_sql` only blocks DML/DDL — it allows `SELECT`, `UNION`, `WITH`. An authenticated user can exfiltrate the entire internal database.
- **Impact**: Complete data exfiltration from internal PostgreSQL — user credentials, datasource configurations, all business data.
- **Evidence**: `test_dataset_routes.py` line 190-203 tests the route with a fake that returns empty arrays, never verifying real SQL execution behavior.
- **Fix**: Remove the fallthrough to internal DB execution when no `datasourceId` is provided. Whitelist allowed tables or use a read-restricted database role.

---

### BUG-045: Unauthenticated Export File Download (IDOR)

- **File**: `app/middleware/whitelist.py`, line 63; `app/routers/export.py`, lines 133-145
- **Description**: `/exportCenter/download` is in `WHITE_PREFIXES` — no authentication required. The endpoint `GET /de2api/exportCenter/download/{task_id}` allows anyone to download exported files by guessing/enumerating task IDs.
- **Impact**: Any unauthenticated user can download export files containing potentially sensitive data.
- **Evidence**: `test_export_routes.py` lines 157-168 confirms download works without auth headers.
- **Fix**: Remove from whitelist, require authentication, or implement signed download URLs with expiry.

---

### BUG-046: Second-Order SQL Injection via `filter_sql` Row Permissions (UNION SELECT)

- **File**: `app/services/row_permission_service.py`, lines 23-35; `app/services/data_permission_service.py`, lines 24-47
- **Description**: `_validate_filter_sql()` only blocks 13 DDL/DML keywords but does NOT block `UNION` or `SELECT`. Since `filter_sql` values are stored in the database and later injected raw (no parameterization) into SQL via `apply_row_filters()`, a crafted filter can break out of the WHERE clause. Confirmed exploit: `filter_sql = "1=1) UNION SELECT password FROM core_user WHERE (1=1"` produces valid SQL that exfiltrates passwords from any table.
- **Impact**: Data exfiltration from any table in the internal database via stored filter rules (requires admin to create row permission rules, but is a defense-in-depth failure).
- **Fix**: Add `union`, `select`, `copy`, `vacuum`, `analyze`, `comment` to `_DANGEROUS_SQL_RE`. Parameterize filter application. Validate filter_sql is a simple `column = value` pattern.

---

### BUG-047: `apply_row_filters` Produces Invalid SQL When Query Has WHERE + LIMIT

- **File**: `app/services/data_permission_service.py`, lines 36-38
- **Description**: When the input SQL already has a `WHERE` clause AND has `LIMIT` appended (which always happens because `_apply_limit` runs first in `sql_executor.py`), `apply_row_filters` matches the existing `WHERE` via regex and appends `AND (filter)` at the END of the SQL — after the `LIMIT`. Result: `SELECT ... WHERE active = 1 LIMIT 1000 AND (tenant_id = 9)` — **invalid SQL**. Every query with an existing WHERE clause AND row-level permissions will fail.
- **Impact**: All data queries with user-defined WHERE clauses and row-level permissions fail at execution.
- **Evidence**: `test_data_permission_service_coverage.py` line 72-75 tests `apply_row_filters` with WHERE but WITHOUT LIMIT, missing the real-world flow where LIMIT is always pre-appended. `test_sql_executor_coverage.py` line 330-331 monkeypatches `apply_row_filters`, hiding this bug.
- **Fix**: Wrap user query in subquery: `SELECT * FROM ({original_sql}) _t WHERE {filters}`.

---

## High (Additional Findings)

### BUG-048: SQL Injection via Dict Key Interpolation in `linkage_repo.py`

- **File**: `app/repositories/linkage_repo.py`, lines 165-187
- **Description**: `create_linkage` and `create_linkage_field` build INSERT statements by interpolating `payload.keys()` directly into SQL column names: `cols = ", ".join(payload.keys())`. While values use parameterized `:key` placeholders, column names are NOT sanitized. If any upstream caller passes user-controlled dict keys, arbitrary SQL injection is possible.
- **Impact**: SQL injection through linkage creation if dict keys are user-controlled.
- **Fix**: Define explicit column whitelists for each table and validate keys before building SQL. Use SQLAlchemy ORM `insert()`.

---

### BUG-049: Mass Assignment in Base Repository `update()` and `create()`

- **File**: `app/repositories/base.py`, lines 32-44
- **Description**: `update()` does `setattr(entity, key, value)` for every key in the payload dict. `create()` does `self.model(**payload)`. No validation of which fields can be set. An attacker who can inject additional keys into a payload dict could set `id`, `create_time`, or other protected columns.
- **Impact**: Potential privilege escalation or data corruption via unexpected field modification.
- **Fix**: Add `_updatable_fields` whitelist to each repository/model and filter payloads.

---

### BUG-050: Export Download Endpoint Has No Authentication (Route-Level)

- **File**: `app/routers/export.py`, lines 133-145
- **Description**: `download_export` has no `Depends(get_current_user)` — it only depends on `get_export_service`. Combined with whitelist entry (BUG-045), any unauthenticated user can download export files.
- **Impact**: Unauthenticated access to exported data.
- **Fix**: Add authentication dependency.

---

### BUG-051: `get_field` Returns 200 with `null` Instead of 404 for Missing Fields

- **File**: `app/routers/dataset_field.py`, lines 61-70
- **Description**: When a field ID doesn't exist, the endpoint returns `{"code": 0, "data": null, "msg": "success"}` — a 200 status with null data. Other get-by-ID endpoints correctly return 404. Callers cannot distinguish "field not found" from "field exists with null data."
- **Impact**: API inconsistency; frontend may show empty state instead of error state.
- **Evidence**: `test_dataset_field_routes.py` lines 208-219 asserts `status_code == 200` and `data is None`.
- **Fix**: Raise `HTTPException(status_code=404)` when field is not found.

---

### BUG-052: Chart `get_data` Swallows All Exceptions, Returns Empty Data

- **File**: `app/services/chart_service.py`, lines 133-135
- **Description**: `except Exception: logger.exception(...)` logs the error but returns an empty chart response (`total=0, data=[]`). Users see an empty chart with no indication of failure.
- **Impact**: Silent errors in chart rendering; users don't know their data query failed.
- **Evidence**: `test_chart_service_coverage.py` lines 552-564 confirms this behavior with `RuntimeError`.
- **Fix**: Include an error indicator in the response so the frontend can display an error state.

---

### BUG-053: Unbounded `list_all_ordered` Query in Visualization Repository

- **File**: `app/repositories/visualization_repo.py`, lines 19-25
- **Description**: `list_all_ordered()` has no `LIMIT` or `WHERE` filter. Loads every `DataVisualizationInfo` row (including large JSONB `component_data` and `canvas_style_data`) into memory. Called from 8+ endpoints: `tree`, `save`, `update`, `save_canvas`, `update_canvas`, `update_base`, `name_check`, `move`.
- **Impact**: Severe latency and memory spikes in production with thousands of visualizations.
- **Fix**: Replace full-table scan with targeted queries per call site. Add `.where(delete_flag.is_(False))` at minimum. For `name_check`, use `SELECT EXISTS(...)`.

---

### BUG-054: Dead-Code Watermark Routes in `visualization.py` (No-Op Save)

- **File**: `app/routers/visualization.py`, lines 472-492; `app/services/visualization_service.py`, lines 1059-1060
- **Description**: `visualization.py` registers `POST /watermark/save` using `VisualizationService.save_watermark` which is a **no-op** (`return {"success": True}`). Meanwhile, `watermark.py` registers the **real** handlers using `WatermarkService`. If router registration order ever changes, watermark save silently stops persisting.
- **Impact**: Silent data loss if registration order changes; confusing dead code.
- **Fix**: Remove duplicate `/watermark/*` routes from `visualization.py`.

---

## Medium (Additional Findings)

### BUG-055: `name_check` Misses Items with `pid=0` (Legacy Java Data)

- **File**: `app/services/visualization_service.py`, lines 823-838
- **Description**: `_normalize_int(payload.pid)` converts `0` → `None`. Items migrated from legacy Java backend may have `pid=0`. When `pid` is `None`, comparison `0 != None` is `True`, so those items are skipped — name collision check fails silently.
- **Impact**: Duplicate names possible under root folder for legacy items.
- **Fix**: Normalize `item.pid` through `_normalize_int` before comparison.

---

### BUG-056: `query_ds_with_visualization_id` Doesn't Recurse into Nested Components

- **File**: `app/services/visualization_service.py`, lines 1038-1046
- **Description**: Only scans top-level items in `component_data` for `datasetId`. Components inside `Group` or `DeTabs` are missed. Dashboards with tabbed layouts report incomplete dataset associations.
- **Impact**: Incomplete dataset tracking for dashboards with nested components.
- **Fix**: Recurse into `propValue.componentData` for Group/DeTabs components.

---

### BUG-057: `query_stores` N+1 Query Problem

- **File**: `app/services/visualization_service.py`, lines 956-971
- **Description**: For each user favorite, does `self.visualization_repo.get_by_id(store.resource_id)` individually. Classic N+1 query pattern.
- **Impact**: Performance degradation proportional to number of user favorites.
- **Fix**: Batch-fetch all visualization records with `WHERE id IN (...)`.

---

### BUG-058: `_compute_level` Silently Produces Level 1 for Non-Existent Parent

- **File**: `app/services/visualization_service.py`, lines 53-57
- **Description**: When `pid` is not found in `all_items`, returns level 1 without error. Moving/saving a visualization to a non-existent parent creates orphaned tree nodes.
- **Impact**: Corrupted tree structures — orphaned children at level 1.
- **Fix**: Validate that `pid` exists before computing level, or raise HTTP 400/404.

---

### BUG-059: Recursive Cascade Delete Without Depth Limit

- **File**: `app/repositories/dataset_repo.py`, lines 36-44
- **Description**: `_delete_descendants` is recursive with no depth limit. A deeply nested dataset tree (1000+ levels) causes Python stack overflow. Each level issues multiple DB queries and commits.
- **Impact**: Stack overflow and partial database state on deeply nested deletes.
- **Fix**: Add max depth parameter (e.g., 50). Use iterative approach or recursive CTE.

---

### BUG-060: `/resource/checkPermission` Always Returns `True`

- **File**: `app/routers/bootstrap.py`, lines 205-211
- **Description**: This endpoint always returns `True`, granting permission to all resources. If the frontend relies on this for UI gating, all resource actions are exposed to all users.
- **Impact**: Permission UI shows all actions enabled for all users.
- **Fix**: Implement actual permission checking or remove the endpoint.

---

### BUG-061: `_normalize_info` Returns Invalid JSON Strings Unparsed

- **File**: `app/services/dataset_service.py`, lines 486-492
- **Description**: When `json.loads()` fails on a stored `info` value, the raw string is returned as-is. Downstream code expecting a dict/list will crash with `AttributeError` when calling `.get()` on a string.
- **Impact**: Unhandled 500 errors for datasets with malformed info JSON.
- **Evidence**: `test_dataset_service_unit.py` lines 232-233 explicitly tests and confirms this behavior.
- **Fix**: Log a warning and return `{}` (empty dict) instead of the raw string.

---

### BUG-062: SQL Log Save Accepts Completely Empty Payload

- **File**: `app/schemas/share.py` (SqlLogCreateRequest); `app/routers/dataset.py`
- **Description**: `POST /datasetTableSqlLog/save` with `{}` returns 200 with all fields as `None`. No required field validation. A SQL log entry with no `table_id`, no `sql_snapshot`, and no `status` is meaningless.
- **Impact**: Database pollution with empty log entries.
- **Evidence**: `test_dataset_sql_log_routes.py` lines 113-131 confirms empty payload accepted.
- **Fix**: Add required field validation to `SqlLogCreateRequest` (at minimum `table_id`).

---

### BUG-063: Delete Export Task Uses GET HTTP Method

- **File**: `app/routers/export.py`, lines 51-58
- **Description**: `@router.get("/delete/{task_id}")` uses GET for deletion. Violates HTTP semantics — can be triggered by crawlers, pre-fetch, or browser history.
- **Impact**: Accidental task deletion via crawlers or browser pre-fetch.
- **Evidence**: `test_export_uncovered_routes.py` lines 153-168 confirms GET deletion works.
- **Fix**: Change to `@router.delete` or `@router.post`.

---

### BUG-064: SysSettingService Methods Return Defaults on Any Error

- **File**: `app/services/sys_setting_service.py`, lines 19-66
- **Description**: Every method catches `(AttributeError, TypeError)` and returns a default value. Database connectivity issues are hidden behind defaults — the system silently runs with defaults instead of failing fast.
- **Impact**: Configuration drift — system runs with wrong settings after DB failures.
- **Evidence**: `test_org_menu_system_coverage.py` lines 265-288 validates this silent fallback.
- **Fix**: Distinguish between "no data" (return default) and "database error" (raise).

---

## Low (Additional Findings)

### BUG-065: Request ID Header Trust Without Validation

- **File**: `app/middleware/request_id.py`, lines 34, 57-61
- **Description**: Reuses `X-Request-ID` from incoming request without validation. An attacker can inject arbitrary content (up to ~8KB) into the header, which gets stored in ContextVar and logged — potential log injection.
- **Fix**: Validate against UUID format, max length 64 chars.

---

## Summary

| Severity | Count | Key Themes |
|----------|-------|------------|
| **Critical** | 9 | Missing auth, SQL injection (3 vectors), share auth bypass, SSRF, internal DB exfiltration, IDOR |
| **High** | 20 | Fail-open permissions, token security, info leakage, OOM vectors, insecure PRNG, dead code, mass assignment |
| **Medium** | 21 | Silent failures, race conditions, data loss, N+1 queries, unbounded queries, API design |
| **Low** | 12 | Rate limiting, performance, MD5, test gaps, edge cases, log injection |

### Top Priority Fixes (Critical + High, ordered by exploitability)

1. **BUG-044**: Block internal DB access in `previewSql` — whitelist tables or use restricted DB role
2. **BUG-001**: Add permission checks to 13 unprotected dataset endpoints
3. **BUG-045/050**: Add authentication to export download endpoint
4. **BUG-004**: Gate link token generation behind successful auth in `proxy_info()`
5. **BUG-005**: Validate ticket UUID against share UUID
6. **BUG-046**: Add UNION/SELECT to `_validate_filter_sql` forbidden keywords
7. **BUG-047**: Fix `apply_row_filters` for WHERE+LIMIT queries (use subquery wrapping)
8. **BUG-002**: Parameterize/escape `table_name` in `preview_data`
9. **BUG-006**: Validate URL scheme in `load_remote_file`
10. **BUG-048**: Whitelist column names in `linkage_repo.py`
11. **BUG-010**: Enforce `ticket_require` in `resolve()` and `/share/view/`
12. **BUG-014/015/016**: Fix token security (unique secrets, remove fallback, add refresh window)
13. **BUG-007/008**: Convert fail-open to fail-closed for permission defaults
