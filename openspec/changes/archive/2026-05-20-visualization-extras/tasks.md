## 1. Visualization compatibility endpoints

- [x] 1.1 Add request schema support for visualization copy, interactive tree filtering, store execute payloads, and any stub response inputs using the existing camelCase/snake_case alias conventions.
- [x] 1.2 Extend the visualization router/service to implement `/dataVisualization/copy`, `/dataVisualization/interactiveTree`, export log stubs, `/panel/view/getComponentInfo/{dvId}`, and `/dataVisualization/export2AppCheck`.
- [x] 1.3 Implement `/store/execute` as a favorite toggle that reuses the current store add/remove logic.

## 2. Backend contract coverage

- [x] 2.1 Extend route tests to verify the new visualization/panel/store endpoints are mounted, authenticated, and return wrapped success payloads.
- [x] 2.2 Add focused service-level coverage for new toggle/filter/copy behavior where route tests alone would not prove the logic.

## 3. Verification

- [x] 3.1 Run `uv run ruff check .` from `core/pydataease-backend/`.
- [ ] 3.2 Run `uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` from `core/pydataease-backend/`.
- [x] 3.3 Run `uv run python -c "from app.main import app; print(app.title)"` from `core/pydataease-backend/`.
