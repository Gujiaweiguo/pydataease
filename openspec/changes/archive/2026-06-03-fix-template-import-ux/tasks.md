## 1. Workflow alignment

- [x] 1.1 Identify the canonical template import experience to keep as the primary entry point for `.DET2` and `.DET2APP` imports.
- [x] 1.2 Update template-related navigation so template management, template market, and resource creation all route users toward the canonical import path.
- [x] 1.3 Remove or relabel ambiguous template actions that make the current import/reuse path appear missing.

## 2. Frontend entry-point implementation

- [x] 2.1 Add a visible import action in the selected template-management/template-workflow surface for supported template files.
- [x] 2.2 Add a user-visible import path or guidance from the local template market so users can reach import without hidden navigation.
- [x] 2.3 Keep existing local-template apply behavior intact while wiring the new import entry points into the same reusable template flow.

## 3. Export and guidance updates

- [x] 3.1 Add or update inline guidance near export/import actions to explain when users should use `.DET2` versus `.DET2APP`.
- [x] 3.2 Make the export workflow point users toward the canonical import path for reusable `.DET2` files.
- [x] 3.3 Ensure the guidance text describes imported templates as part of the local template library workflow, not as an unrelated file operation.

## 4. Verification

- [x] 4.1 Run frontend fast checks: `cd core/core-frontend && npm run ts:check && npm run lint && npm run lint:stylelint`.
- [x] 4.2 If routing or packaging-visible behavior changes, run frontend build verification: `cd core/core-frontend && npm run build:distributed`.
- [x] 4.3 Manually verify the export → import → local reuse flow in the running UI, including template management entry, template market guidance, and local template apply behavior.
- [x] 4.4 If implementation changes backend contracts or response handling, run backend validation: `cd core/pydataease-backend && uv run ruff check . && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`.
