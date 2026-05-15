## ADDED Requirements

### Requirement: Menu query SHALL return the navigation tree for authenticated users
The backend SHALL expose `GET /de2api/menu/query` that returns a tree of menu entries for the currently authenticated user.

#### Scenario: Admin user queries menu tree
- **WHEN** an authenticated user sends `GET /de2api/menu/query` with a valid `X-DE-TOKEN`
- **THEN** the backend SHALL return status 200 with a JSON array of root-level MenuVO objects, each potentially containing nested children

#### Scenario: Unauthenticated user queries menu tree
- **WHEN** a request is made without `X-DE-TOKEN` header
- **THEN** the response SHALL have status 401

#### Scenario: Menu tree structure matches frontend expectations
- **WHEN** the menu tree is returned
- **THEN** each MenuVO SHALL contain: `path`, `component`, `hidden`, `isPlugin`, `name`, `inLayout`, `redirect` (nullable), `meta` object with `title` and `icon`, and `children` array

### Requirement: Database SHALL store menu entries in core_menu table
The backend SHALL create a `core_menu` table with columns: id (BigInteger PK), pid (BigInteger), type (Integer), name (String), component (String), menu_sort (Integer), icon (String nullable), path (String), hidden (Boolean), in_layout (Boolean), auth (Boolean).

#### Scenario: Migration creates core_menu with community seed data
- **WHEN** `alembic upgrade head` runs
- **THEN** the `core_menu` table SHALL exist with at least these menus: workbranch, panel, screen, data (with dataset+datasource children), system settings

### Requirement: Additional workbranch stubs SHALL prevent 404 errors
The backend SHALL provide stub responses for endpoints called by the workbranch page.

#### Scenario: Share base settings requested
- **WHEN** `GET /de2api/sysParameter/shareBase` is called
- **THEN** the response SHALL return `{"disable": true, "peRequire": false}`

#### Scenario: Template market recommendations requested
- **WHEN** `GET /de2api/templateMarket/searchRecommend` is called
- **THEN** the response SHALL return `{"baseUrl": "", "contents": []}`

#### Scenario: Business interactive tree requested
- **WHEN** `POST /de2api/dataVisualization/interactiveTree` is called
- **THEN** the response SHALL return `{"dashboard": [], "dataV": [], "dataset": [], "datasource": []}`

#### Scenario: Typeface endpoints requested
- **WHEN** `GET /de2api/typeface/defaultFont` or `GET /de2api/typeface/listFont` is called
- **THEN** the response SHALL return `[]`
