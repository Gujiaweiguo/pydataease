## Why

The shared Vue frontend already calls several visualization, panel, and store endpoints that the FastAPI backend does not expose yet, leaving important dashboard flows broken or partially stubbed during the Python migration. This change closes that contract gap now so visualization copy, embedded panel helpers, interactive tree access, export prechecks, and favorite toggles behave consistently without forcing frontend workarounds.

## What Changes

- Add the missing visualization and panel routes required by the frontend contract, including copy, interactive tree, export-log stubs, embedded component info, and export-to-app precheck behavior.
- Add the missing store execute route so favorite/unfavorite actions can toggle persisted store records through the FastAPI backend.
- Reuse existing visualization and store service/repository logic where available, adding only the minimal service/schema support needed for the missing contract surface.
- Extend backend route tests to verify the new endpoints are mounted, authenticated, and wrapped with the standard `ResultMessage` response envelope.
- Verify this API/backend change with L0 backend (`uv run ruff check .`) and L1 backend (`uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`) gates plus the FastAPI import check, because the work changes authenticated routes and service behavior but not packaging or release flows.

## Capabilities

### New Capabilities
- `visualization-extras`: Provide frontend-required visualization/panel/store API compatibility endpoints that are currently missing from the FastAPI backend.

### Modified Capabilities
- `backend-contract-compatibility`: Extend route-level contract coverage so newly implemented visualization extras endpoints are tested as supported APIs instead of remaining uncovered.

## Impact

- Affected backend code: `core/pydataease-backend/app/routers/visualization.py`, `app/services/visualization_service.py`, related schemas/repositories, and route tests under `core/pydataease-backend/tests/`.
- Affected API surface: `/dataVisualization/*`, `/panel/view/getComponentInfo/{dvId}`, and `/store/execute` under `/de2api`.
- No new infrastructure or external dependencies; export log and embedded panel helpers remain explicit compatibility stubs for now.
