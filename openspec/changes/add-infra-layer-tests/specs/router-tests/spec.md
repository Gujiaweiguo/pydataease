## ADDED Requirements

### Requirement: Router configuration tests
The test suite SHALL verify that the router is configured with the correct routes, hash history mode, and expected route paths.

#### Scenario: Router uses createWebHashHistory
- **WHEN** the router module is loaded
- **THEN** it SHALL export a router instance using `createWebHashHistory`

#### Scenario: Expected static routes are registered
- **WHEN** inspecting the router's route records
- **THEN** the following route paths SHALL be present: `/login`, `/admin-login`, `/401`, `/workbranch`, `/sqlbot`, `/dvCanvas`, `/dashboard`, `/dashboardPreview`

#### Scenario: Login route is registered
- **WHEN** the router configuration is loaded
- **THEN** a route with path `/login` and name `login` SHALL exist

#### Scenario: Router setup registers on app
- **WHEN** `setupRouter(app)` is called
- **THEN** `app.use(router)` SHALL be called

### Requirement: Navigation guard tests
The test suite SHALL verify the navigation guard behavior in `src/permission.ts`, focusing on the whitelist logic and redirect behavior.

#### Scenario: Whitelist routes are accessible without token
- **WHEN** navigating to a whitelist path (`/login`, `/de-link/*`, `/chart-view`, `/admin-login`, `/401`)
- **THEN** the guard SHALL call `next()` allowing navigation

#### Scenario: Unknown routes redirect to login without token
- **WHEN** navigating to a non-whitelist path without a user token and not in desktop mode
- **THEN** the guard SHALL redirect to `/login?redirect=<original-path>`

#### Scenario: Authenticated user visiting login redirected to workbranch
- **WHEN** a user with a valid token navigates to `/login`
- **THEN** the guard SHALL redirect to `/workbranch/index`

#### Scenario: Embedded token allows embedded routes
- **WHEN** the embedded store has a token and the app is in iframe mode
- **THEN** the guard SHALL allow navigation to embedded whitelist routes

#### Scenario: 401 route is always accessible
- **WHEN** navigating to `/401`
- **THEN** the guard SHALL allow navigation regardless of token status

### Requirement: Route generation utility tests
The test suite SHALL verify the route generation utilities in `src/router/establish.ts`.

#### Scenario: generateRoutesFn2 resolves Layout component
- **WHEN** a route has `component: 'Layout'`
- **THEN** `generateRoutesFn2` SHALL assign the Layout import function as the component

#### Scenario: generateRoutesFn2 resolves view components
- **WHEN** a route has a view component path
- **THEN** `generateRoutesFn2` SHALL resolve it from the views glob import

#### Scenario: formatRoute flattens single-child routes
- **WHEN** a route has exactly one child and path is not `/data`
- **THEN** `formatRoute` SHALL merge the child path into the parent
