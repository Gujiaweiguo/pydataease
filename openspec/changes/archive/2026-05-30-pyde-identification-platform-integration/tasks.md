## 1. Identification Settings Backbone (T11)

- [x] 1.1 Define the authentication settings backend model: default login method, enabled provider list, provider status query contract, admin configuration endpoints, and failure fallback rules to local login
- [x] 1.2 Define responsibility boundary between local login and external providers: organization mapping, user mapping, and provider disable/enable strategy
- [x] 1.3 Design the `/setting/authentication/status` evolution from empty-array stub to stable status interface describing provider enable/disable states and default login selection
- [x] 1.4 Define the provider registry as an abstraction layer (LDAP / OIDC / CAS unified contract), not a one-shot implementation of all vendors

## 2. Platform Integration Adapter Strategy (T12)

- [x] 2.1 Define the provider adapter contract: configuration persistence, enable/disable lifecycle, callback handling, declarative claim mapping, error fallback, and local account fallback
- [x] 2.2 Abstract LDAP, OIDC, and CAS into a unified provider contract to avoid parallel implementation paths
- [x] 2.3 Define the minimum deliverable for first release: interface skeleton, configuration persistence, status exposure, test contract, and at least one end-to-end provider mock
- [x] 2.4 Define the implementation boundary that does not depend on `de-xpack/` and list explicitly deferred items

## 3. Verification

- [x] 3.1 `cd core/pydataease-backend && uv run ruff check .`
- [x] 3.2 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] 3.3 `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
- [x] 3.4 Verify identification backbone documentation exists:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  for marker in ['default login', 'provider', '/setting/authentication/status', '本地登录']:
      assert marker in text or marker.lower() in text.lower()
  print('Identification backbone verified')
  "
  ```
- [x] 3.5 Verify local-login fallback is preserved:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  assert '安全回退' in text or '本地登录作为安全回退' in text
  print('Local login fallback verified')
  "
  ```
- [x] 3.6 Verify provider adapter contract documentation:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  for marker in ['LDAP', 'OIDC', 'CAS', 'adapter', 'mock']:
      assert marker in text or marker.lower() in text.lower()
  print('Provider adapter contract verified')
  "
  ```
- [x] 3.7 Verify xpack independence:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  assert '不依赖 \`de-xpack/\`' in text or 'de-xpack' in text
  print('xpack independence verified')
  "
  ```
