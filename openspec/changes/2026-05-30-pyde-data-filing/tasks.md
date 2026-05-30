## 1. Data Filing Domain Model and Write-Path Safety (T13)

- [x] 1.1 Define the data filing domain model: form/filing configuration, published state, submission records, status records, audit records, error codes, and idempotency strategy
- [x] 1.2 Establish that `enable_data_fill` is a capability flag only (not a complete implementation); define supplementary datasource/engine write-back constraints, field validation, and permission layering
- [x] 1.3 Define the minimum viable filing workflow priority: admin configuration, publish, submit, query, audit
- [x] 1.4 Define dependencies on system variables (parameterized forms), embedding context (embedded filing forms), and authentication settings (submitter identity)
- [x] 1.5 Define ACL model: separate permissions for submit, manage, view, and audit operations
- [x] 1.6 Define audit model: who submitted, when, what data, to which datasource, success/failure status, and retry history

## 2. Data Filing Admin Workflow (T14)

- [x] 2.1 Define admin capabilities: create filing configuration, publish, disable, assign permissions, view records, and retry/replay on exception
- [x] 2.2 Define the minimum user workflow and embed/public access boundaries
- [x] 2.3 Define failure scenarios and handling: field validation failure, target datasource not writable, permission denied, duplicate submission, partial write failure
- [x] 2.4 Define the first-release deliverable surface and explicitly list deferred items
- [x] 2.5 Enforce prohibition of anonymous public writes

## 3. Verification

- [x] 3.1 `cd core/pydataease-backend && uv run ruff check .`
- [x] 3.2 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] 3.3 `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
- [x] 3.4 Verify data filing safety model documentation:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  for marker in ['数据填报', 'ACL', '审计', '幂等', '失败恢复']:
      assert marker in text
  print('Data filing safety model verified')
  "
  ```
- [x] 3.5 Verify flag-only implementation is rejected:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  assert '不是完整能力' in text or '不把数据填报当作简单的 datasource 开关' in text
  print('Flag-only rejection verified')
  "
  ```
- [x] 3.6 Verify data filing workflow coverage:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  for marker in ['创建', '发布', '停用', '记录查看', '重复提交']:
      assert marker in text
  print('Data filing workflow coverage verified')
  "
  ```
- [x] 3.7 Verify anonymous write is prohibited:
  ```
  cd core/pydataease-backend && python3 -c "
  from pathlib import Path
  text = Path('../../.sisyphus/plans/pydataease-dataease-capabilities-plan-v1.md').read_text()
  assert '不允许公开匿名写入' in text or '匿名公开写入被禁止' in text
  print('Anonymous write prohibition verified')
  "
  ```
