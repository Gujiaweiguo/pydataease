## 1. Appearance Configuration

- [x] T05. Close appearance configuration gaps
  - Define the complete appearance configuration item inventory: site name, theme color, navbar style, login page image references, footer text, help link, demo tip, font configuration.
  - Specify which items use existing `basic.*` / `ui` keys and which need new keys or structured configuration.
  - Define persistence strategy, default values, fallback values, cache refresh, and public-page read behavior for each item.
  - Define visibility rules: which configuration changes affect normal pages, login pages, share pages, and embedded pages.
  - **Must NOT**: copy DataEase original assets; expand appearance configuration into a full-site UI redesign project.

## 2. Watermark Runtime

- [x] T06. Integrate watermark runtime policy
  - Define watermark admin save contract: authenticated admin-only write, validated payload, persistent storage.
  - Define watermark public read contract: what fields are visible to unauthenticated clients, what is redacted.
  - Define runtime display rules for each context: normal pages (logged in), share pages (public), embedded pages (with and without login).
  - Define watermark text template placeholder rules and integration with system variables.
  - Define safe rollback: disabling watermark flag turns off display without deleting saved configuration.
  - **Must NOT**: fork watermark logic into multiple runtime versions; let public query endpoints expose unnecessary sensitive information.

## 3. Verification

- [x] V1. `cd core/pydataease-backend && uv run ruff check .`
- [x] V2. `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] V3. `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
- [x] V4. If admin UI is touched: `cd core/core-frontend && npm run ts:check && npm run lint`
