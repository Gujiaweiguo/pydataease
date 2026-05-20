## Context

The FastAPI backend already follows a consistent router → service → repository → model structure, but `sysVariable` does not exist yet while the shared frontend already expects its CRUD endpoints. The backend also splits `sysParameter` behavior across `system.py`, `bootstrap.py`, `SystemService`, and `SysSettingService`, leaving a few compatibility gaps for map settings and bootstrap configuration endpoints.

This change is cross-cutting because it adds a new persisted module, extends router registration, and fills frontend contract gaps in the same area of system configuration. The implementation must stay compatible with the current response wrapper, auth middleware, async SQLAlchemy patterns, and camelCase schema serialization used elsewhere in the backend.

## Goals / Non-Goals

**Goals:**
- Add a first-pass `sysVariable` module with variable-definition CRUD and variable-value CRUD endpoints.
- Persist variable definitions and values with new SQLAlchemy models that follow the existing BigInteger/time-based ID convention.
- Keep the implementation lightweight and backend-native: async repositories, service-layer validation, and route tests using dependency overrides.
- Complete the missing `sysParameter` endpoints by reusing existing in-memory/system-setting infrastructure instead of inventing a separate config subsystem.
- Verify the slice with L0 backend checks plus targeted route/auth tests and app import validation.

**Non-Goals:**
- Creating or applying Alembic migrations in this session.
- Building frontend screens or wiring the frontend to the new endpoints.
- Implementing advanced variable execution semantics such as SQL interpolation, permission scoping, or dataset-aware validation beyond storing related IDs.
- Expanding verification to release-sensitive Docker or runnable-environment gates.

## Decisions

### 1. Store sysVariable as two additive models with a parent-child relationship
Use `CoreSysVariable` for the variable definition and `CoreSysVariableValue` for selectable values, linked by `variable_id`.

**Why:** The requested API surface naturally splits metadata from option values, and separate tables align with the existing repository/service patterns.

**Alternatives considered:**
- **Single JSON column on the variable record:** rejected because it would complicate CRUD, pagination, and future relational filtering.
- **No persistence, in-memory stubs only:** rejected because the requested module is intended to back real user-managed variables.

### 2. Keep service validation simple and synchronous-with-request
The service layer will own ID/timestamp generation, missing-record checks, and response shaping, while repositories remain thin data-access wrappers.

**Why:** This matches the current backend design and keeps route handlers minimal.

**Alternatives considered:**
- **Fat repositories with business logic:** rejected because it would diverge from the project’s existing layering.
- **Direct router-to-repository access:** rejected because auth-aware validation and payload normalization belong in services.

### 3. Reuse existing sys setting services for sysParameter compatibility
Missing `/sysParameter` endpoints will delegate to `SystemService` or `SysSettingService` depending on whether the data is in-memory runtime config or persisted key/value settings.

**Why:** The codebase already has two partial implementations of system parameter behavior; completing the contract is lower risk than introducing a third path.

**Alternatives considered:**
- **Create a new sys-parameter service module:** rejected as unnecessary duplication.
- **Move everything into one service now:** rejected because that refactor is broader than the compatibility goal.

### 4. Use route-level tests with fake services for contract coverage
Tests will validate registration, response wrapping, and auth requirements by overriding service dependencies rather than requiring a database.

**Why:** This is the repo’s established contract-testing pattern and avoids blocking on migrations that are explicitly deferred.

**Alternatives considered:**
- **Repository or integration tests only:** rejected because the immediate risk is frontend contract breakage, not deep query behavior.

## Risks / Trade-offs

- **[Risk] New models exist without a migration in the same change** → **Mitigation:** keep the change additive and document migration generation as follow-up work.
- **[Risk] SysParameter behavior stays split across two services** → **Mitigation:** only extend the existing ownership boundaries and keep endpoint delegation explicit.
- **[Risk] Variable query semantics may differ from future frontend expectations** → **Mitigation:** implement generic search/pagination-safe CRUD shapes now and leave advanced filtering rules to follow-up changes.
- **[Risk] Targeted tests may miss unrelated backend regressions** → **Mitigation:** preserve route/auth assertions and note broader L1 regression as recommended follow-up verification.
