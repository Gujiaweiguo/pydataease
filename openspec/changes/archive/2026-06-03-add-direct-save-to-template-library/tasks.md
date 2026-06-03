## 1. Direct-save workflow setup

- [x] 1.1 Identify the visualization surfaces that should expose the new direct-save-to-template-library action.
- [x] 1.2 Define the direct-save interaction flow, including how users enter the action and how they confirm save success.
- [x] 1.3 Reuse or extract shared template-payload construction logic so direct save and file export do not drift.

## 2. Frontend direct-save implementation

- [x] 2.1 Add a dedicated "save to template library" action in the selected dashboard and screen visualization UI.
- [x] 2.2 Implement the metadata prompt for template name and destination category with sensible defaults.
- [x] 2.3 Submit the constructed template payload through the existing or minimally extended template save contract instead of downloading a file.

## 3. Backend and local-library integration

- [x] 3.1 Validate that the current template save API accepts the fields needed for directly saved templates, and extend it only if required.
- [x] 3.2 Ensure directly saved templates persist into `visualization_template` with the data needed for preview, listing, and reuse.
- [x] 3.3 Verify directly saved templates appear in template management and local template market queries with normal `source=manage` behavior.
- [x] 3.4 Verify directly saved templates can be applied through the existing local-template apply flow without special-case handling.

## 4. Verification

- [x] 4.1 Run frontend fast checks: `cd core/core-frontend && npm run ts:check && npm run lint && npm run lint:stylelint`.
- [x] 4.2 Run backend validation for template persistence behavior: `cd core/pydataease-backend && uv run ruff check . && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`.
- [x] 4.3 If routing or packaged frontend behavior changes materially, run: `cd core/core-frontend && npm run build:distributed`.
- [x] 4.4 If implementation adds schema changes or migration-sensitive persistence changes, run: `cd core/pydataease-backend && uv run alembic upgrade head`.
- [x] 4.5 Manually verify the full direct-save flow: save an existing dashboard, save an existing screen, confirm both appear in template management/template market, and confirm both can be applied later.
