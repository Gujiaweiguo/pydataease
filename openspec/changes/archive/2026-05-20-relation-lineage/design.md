## Context

The FastAPI backend already exposes authenticated routers under `/de2api` and uses direct SQLAlchemy model queries for simple lookup endpoints. Relation/lineage lookups only need read-only traversal across existing tables: datasource-backed dataset tables (`core_dataset_table`) and chart views (`core_chart_view`). The change must fit the current router registration pattern, preserve auth enforcement via `get_current_user`, and keep verification lightweight with backend lint, targeted route tests, and app import smoke coverage.

## Goals / Non-Goals

**Goals:**
- Add three authenticated relation endpoints that return lightweight lineage objects for datasource, dataset group, and visualization lookups.
- Reuse existing async database/session dependencies and SQLAlchemy models without new repositories or migrations.
- Cover route registration and unauthenticated access behavior with focused tests.

**Non-Goals:**
- No recursive lineage graph, pagination, filtering, or cross-service aggregation.
- No frontend wiring or changes to response-wrapper middleware behavior.
- No schema migrations, authorization model changes, or data enrichment beyond fields already stored on the linked records.

## Decisions

### Decision: Implement lineage as a standalone router
Create `app/routers/relation.py` and register it with the existing API router in `app/main.py`.

- **Why:** The endpoints are a cohesive API surface and match the repository's router-per-domain convention.
- **Alternative considered:** Adding these handlers to `dataset.py` or `visualization.py` would blur responsibilities and make future lineage expansion harder.

### Decision: Query existing ORM models directly inside the route handlers
Use `CoreDatasetTable` and `CoreChartView` with simple `select(...)` statements in the router.

- **Why:** The requested behavior is read-only, narrow in scope, and aligns with existing thin-router/simple-query patterns already used in the backend.
- **Alternative considered:** Introducing a dedicated relation service/repository layer would add indirection without reducing complexity for three single-query endpoints.

### Decision: Return compact relation dictionaries with string IDs
Return list payloads containing only the fields the caller needs (`id`, `name`, `type`, plus `sceneId` or `tableId` where applicable), coercing identifiers to strings.

- **Why:** This matches the requested contract, avoids exposing ORM objects directly, and keeps large integer serialization consistent with other backend responses.
- **Alternative considered:** Defining new response schemas was unnecessary for this small, stable payload shape.

### Decision: Verify via focused contract/auth tests
Add `tests/test_relation_routes.py` to assert route mounting and missing-auth behavior, then run L0 lint, targeted pytest, and app import smoke.

- **Why:** This is an authenticated API contract change, so route presence and auth enforcement are the minimum meaningful regression checks.
- **Alternative considered:** Running the entire backend suite is heavier than required for this scoped change.

## Risks / Trade-offs

- **[Risk] Duplicate dataset-group rows from datasource lookup if multiple dataset tables share the same group** → **Mitigation:** Accept current record-per-table behavior for parity with the requested implementation; refine later if callers require de-duplication.**
- **[Risk] Thin-router queries bypass service-layer abstractions** → **Mitigation:** Keep the endpoints narrowly scoped and isolated in their own router so service extraction remains easy if lineage logic grows.**
- **[Risk] Tests validate auth failures but not successful DB-backed responses** → **Mitigation:** Treat this as sufficient for the initial contract addition; add fixture-backed success cases when stable seeded data becomes available.**
