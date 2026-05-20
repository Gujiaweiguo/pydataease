## ADDED Requirements

### Requirement: Visualization compatibility endpoints SHALL be available to the shared frontend
The FastAPI backend SHALL expose the missing visualization and panel compatibility endpoints required by the shared Vue frontend under the existing `/de2api` API prefix, using the standard auth middleware and `ResultMessage` response wrapper.

#### Scenario: Copy endpoint duplicates a visualization resource
- **WHEN** an authenticated client posts to `/de2api/dataVisualization/copy` with a valid source visualization identifier and business flag
- **THEN** the backend SHALL create a duplicated visualization resource with a new identifier based on the existing source visualization payload and return the copied resource metadata in a wrapped success response

#### Scenario: Interactive tree endpoint narrows results by business flag
- **WHEN** an authenticated client posts to `/de2api/dataVisualization/interactiveTree` with a supported `busiFlag`
- **THEN** the backend SHALL return only the tree branch relevant to that business flag in a wrapped success response

#### Scenario: Export compatibility helpers respond without logging infrastructure
- **WHEN** an authenticated client posts to `/de2api/dataVisualization/exportLogApp`, `/exportLogTemplate`, `/exportLogPDF`, or `/exportLogImg`
- **THEN** each endpoint SHALL return an empty list in a wrapped success response

#### Scenario: Embedded panel helpers expose contract-safe stubs
- **WHEN** an authenticated client calls `/de2api/panel/view/getComponentInfo/{dvId}` or posts to `/de2api/dataVisualization/export2AppCheck`
- **THEN** the backend SHALL return an empty object for component info and `{ "status": "ok" }` for the export precheck in wrapped success responses

### Requirement: Store execute SHALL toggle favorite state
The FastAPI backend SHALL expose `/de2api/store/execute` as a compatibility toggle that adds a store record when the resource is not favorited and removes it when the resource is already favorited.

#### Scenario: Toggle adds a missing favorite
- **WHEN** an authenticated client posts to `/de2api/store/execute` for a resource that is not currently favorited by the user
- **THEN** the backend SHALL create the favorite and return a wrapped response showing `favorited: true`

#### Scenario: Toggle removes an existing favorite
- **WHEN** an authenticated client posts to `/de2api/store/execute` for a resource that is already favorited by the user
- **THEN** the backend SHALL remove the favorite and return a wrapped response showing `favorited: false`
