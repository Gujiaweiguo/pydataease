## 1. Parameter Resolution Contract

- [x] T07. Define canonical parameter resolution contract
  - Design a five-stage resolution chain: source identification, parsing, normalization, injection, and audit.
  - Define priority rules for parameter sources: embedding context > outer params > system variables > default values > template placeholders, with documented override semantics.
  - Define conflict resolution: when two sources provide the same parameter key, the higher-priority source wins.
  - Define null/empty handling: required parameters that resolve to null produce explicit error feedback; optional parameters fall back to defaults.
  - Define required-field enforcement: which parameters must have a value, and what error code is returned when they don't.
  - Output one canonical contract document referenced by Changes 3, 5, and 6.
  - **Must NOT**: allow different pages to define their own priority rules; merge system parameter and system variable storage semantics.

## 2. Variable Governance

- [x] T08. Link system variables to parameter governance
  - Define system variable naming conventions, type classification, and dataset field binding rules.
  - Define variable value management: creation, editing, deletion, and validation against the parameter contract.
  - Define how variables serve runtime contexts: watermark text, embedding parameter injection, platform identity context, and future data filing.
  - Define variable CRUD consistency with the parameter contract: all variable mutations respect the resolution chain and permission boundaries.
  - Define admin console extension points and risk boundaries for variable management.
  - **Must NOT**: let system variables take over all system parameter responsibilities; allow variable resolution to bypass permission or dataset binding validation.

## 3. Verification

- [ ] V1. `cd core/pydataease-backend && uv run ruff check .`
- [ ] V2. `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [ ] V3. `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
