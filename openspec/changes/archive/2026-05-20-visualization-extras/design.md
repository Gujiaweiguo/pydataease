## Context

The FastAPI visualization router already covers most dashboard CRUD and linkage flows, but the shared frontend still calls a small set of legacy compatibility endpoints that were never migrated. Most missing endpoints are thin wrappers over existing visualization/store logic or explicit stubs, so the main design concern is preserving the Vue contract without introducing duplicate persistence patterns or speculative infrastructure.

This work touches multiple backend layers: router wiring, request schemas, visualization/store service methods, and route tests. Because these are authenticated `/de2api` endpoints used by the shared frontend, the change requires L0 backend verification (`uv run ruff check .`) plus L1 backend verification (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`) and the FastAPI import check. No database migration, packaging, or Docker-specific validation is required.

## Goals / Non-Goals

**Goals:**
- Expose the missing frontend-called visualization, panel, and store endpoints from the FastAPI backend.
- Reuse existing visualization retrieval/copy and store persistence helpers instead of adding parallel code paths.
- Keep stub endpoints intentionally minimal but contract-correct so frontend callers stop failing.
- Add route coverage that proves the endpoints are mounted, authenticated, and return wrapped responses.

**Non-Goals:**
- Build a real export-log subsystem or embedded panel component introspection service.
- Redesign the visualization tree/permission model beyond the busiFlag filtering needed by the current frontend contract.
- Change frontend code, database schema, or Java legacy backend behavior.

## Decisions

### Decision: implement the missing endpoints inside the existing visualization router/service surface
The missing APIs all belong to visualization-adjacent flows already centered in `visualization.py` and `VisualizationService`. Keeping them there avoids fragmenting route ownership and lets the existing auth dependency, response wrapper, and repository wiring apply automatically.

**Alternative considered:** create a separate compatibility router/service for legacy endpoints. Rejected because the endpoints are too small, would duplicate dependency wiring, and would make future consolidation harder.

### Decision: treat export-log, export2AppCheck, and embedded component info as explicit compatibility stubs
The frontend needs stable shapes now, but the backend has no real export logging or embed metadata system yet. Returning empty arrays/objects and a simple `{status: "ok"}` check preserves behavior without inventing persistence or fake side effects.

**Alternative considered:** infer pseudo-results from existing data. Rejected because it would create undocumented semantics that are harder to replace later than explicit no-op stubs.

### Decision: implement copy by cloning the existing visualization record through current repository/service helpers
`find_copy_resource` already resolves the frontend-facing payload for a source visualization. The copy endpoint should build on the same source lookup, create a new visualization ID, keep the copied canvas/component payload, and stamp the current user/time fields so the duplicate behaves like a newly created resource.

**Alternative considered:** require the client to resubmit a full save payload after `findCopyResource`. Rejected because the frontend already expects a direct backend copy action.

### Decision: implement `/store/execute` as a toggle over existing add/remove store operations
Store persistence already has `favorited`, `add_store`, and `remove_store`. The execute route can simply inspect current favorite state and call the appropriate existing method, which keeps favorite semantics centralized and consistent with existing store APIs.

**Alternative considered:** make `/store/execute` write directly through the repository. Rejected because it would duplicate toggle rules and bypass the existing response shape.

### Decision: implement `interactiveTree` as a filtered compatibility view over current resource data
The frontend only needs the tree filtered by `busiFlag`; it does not need a new resource discovery backend. The implementation can map supported busiFlags to the existing visualization or non-visualization tree sources and return only the requested branch, while keeping unsupported flags safely empty.

**Alternative considered:** always return the full multi-root interactive tree. Rejected because it ignores the frontend contract and permission-oriented narrowing described in the legacy behavior.

## Risks / Trade-offs

- **[Risk] Copying visualization records without duplicating related charts exactly as legacy Java did** → Mitigation: keep copy behavior scoped to the current FastAPI visualization model and reuse existing serialized source payload, matching the frontend's immediate need for duplicated resources rather than deep export/import parity.
- **[Risk] Stub endpoints could be mistaken for complete features** → Mitigation: keep their responses deliberately simple and document them in specs/design as compatibility stubs.
- **[Risk] `interactiveTree` filtering may not match every historical permission nuance** → Mitigation: align busiFlag mapping with the current FastAPI resource model and cover route registration/response shape now; deeper permission semantics can be extended later without breaking the endpoint contract.
- **[Risk] New request schemas may drift from frontend camelCase payloads** → Mitigation: follow the existing `AliasChoices(..., ...)` and `serialization_alias` patterns used throughout `app.schemas.visualization`.
