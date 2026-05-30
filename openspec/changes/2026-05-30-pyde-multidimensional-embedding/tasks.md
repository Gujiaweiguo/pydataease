## 1. Embed/Share Runtime Context Unification (T09)

- [x] 1.1 Define a unified runtime context model covering share access, link access, and embed access, with explicit token header responsibility boundaries (`X-DE-TOKEN`, `X-DE-LINK-TOKEN`, `X-EMBEDDED-TOKEN`) and fallback rules
- [x] 1.2 Document outer params, jump params, busiFlag, resource type, share expiry, and ticket validation runtime semantics within the unified context
- [x] 1.3 Define error scenarios and responses: expired share, invalid ticket, wrong password, iframe context not allowed, resource unavailable
- [x] 1.4 Verify no second authentication header or embed protocol is introduced, and that share/embed produce compatible parameter contexts

## 2. Multidimensional Embedding Control Plane (T10)

- [x] 2.1 Define the embedding control plane model covering Dashboard, Chart, DataV, and Data Filing (reserved) resource types, with admin-facing configuration for resource-level switches, domain policies, password/ticket/expiry rules, and embed parameter injection
- [x] 2.2 Define link jump routing rules and how they connect to the unified runtime context
- [x] 2.3 Plan the embed admin configuration surface and runtime validation strategy
- [x] 2.4 Define the minimum deliverable surface for Change 5 and explicitly list deferred items

## 3. Verification

- [x] 3.1 `cd core/pydataease-backend && uv run ruff check .`
- [x] 3.2 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] 3.3 `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
- [x] 3.4 Verify token-path unification documentation exists:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  for marker in ['X-DE-LINK-TOKEN', 'X-EMBEDDED-TOKEN', 'share', 'embed']:
      assert marker in text
  print('Token-path unification verified')
  "
  ```
- [x] 3.5 Verify no second embed auth path is documented:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  assert '不新增第二套认证头' in text or '不得新造第二套认证' in text
  print('No second auth path verified')
  "
  ```
- [x] 3.6 Verify embedding control-plane covers all four resource types:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  for marker in ['Dashboard', 'Chart', 'DataV', 'Data Filing']:
      assert marker in text
  print('Embedding control-plane coverage verified')
  "
  ```
