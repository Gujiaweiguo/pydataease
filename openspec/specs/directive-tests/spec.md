## ADDED Requirements

### Requirement: Permission directive tests
The test suite SHALL verify that the `checkPermission` directive function correctly shows or hides elements based on interactive store permissions (menuAuth + anyManage for each flag).

#### Scenario: Element kept when user has all required permissions
- **WHEN** `v-permission` is bound with `['panel']` and `interactiveStore.getData` returns data where the panel entry has both `menuAuth` and `anyManage` as truthy
- **THEN** the element SHALL remain in the DOM

#### Scenario: Element removed when user lacks any required permission
- **WHEN** `v-permission` is bound with `['panel']` and the panel entry lacks `menuAuth` or `anyManage`
- **THEN** the element SHALL be removed from the DOM via `el.parentNode.removeChild(el)`

#### Scenario: Multiple permission codes require ALL to pass
- **WHEN** `v-permission` is bound with `['panel', 'screen']` and the user has permission for panel but not screen
- **THEN** the element SHALL be removed (uses `every`, not `some`)

#### Scenario: Non-array value throws error
- **WHEN** `v-permission` is bound with a non-array value (e.g., a string)
- **THEN** the directive SHALL throw an Error with usage message

#### Scenario: Permission flags are panel, screen, dataset, datasource
- **WHEN** the directive reads permissions from the interactive store
- **THEN** it SHALL map store data indices to flags `['panel', 'screen', 'dataset', 'datasource']`

### Requirement: ClickOutside directive tests
The test suite SHALL verify that the `vClickOutside` directive object correctly handles click-outside behavior via `beforeMount` and `unmounted` hooks.

#### Scenario: Click outside triggers callback
- **WHEN** a click event fires on `document` targeting an element outside the bound element
- **THEN** the bound callback function SHALL be called with the event

#### Scenario: Click inside does not trigger callback
- **WHEN** a click event fires on `document` targeting an element inside (or equal to) the bound element
- **THEN** the bound callback function SHALL NOT be called

#### Scenario: Event listener added on beforeMount
- **WHEN** the directive's `beforeMount` hook runs
- **THEN** a `click` event listener SHALL be registered on `document`

#### Scenario: Event listener removed on unmounted
- **WHEN** the directive's `unmounted` hook runs
- **THEN** the `click` event listener SHALL be removed from `document`
