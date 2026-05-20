## MODIFIED Requirements

### Requirement: Unimplemented endpoints SHALL be explicitly skipped
Contract tests for endpoints not yet implemented in the Python backend SHALL be marked with `pytest.mark.skip` with a descriptive reason, not silently removed.

#### Scenario: Test suite runs against partially implemented backend
- **WHEN** the backend contract and route test suites execute after the visualization extras change is implemented
- **THEN** the newly supported visualization compatibility endpoints (`/de2api/dataVisualization/copy`, `/de2api/dataVisualization/interactiveTree`, `/de2api/dataVisualization/exportLogApp`, `/de2api/dataVisualization/exportLogTemplate`, `/de2api/dataVisualization/exportLogPDF`, `/de2api/dataVisualization/exportLogImg`, `/de2api/panel/view/getComponentInfo/{dvId}`, `/de2api/dataVisualization/export2AppCheck`, and `/de2api/store/execute`) SHALL run as implemented endpoint tests rather than being treated as missing or skipped coverage
