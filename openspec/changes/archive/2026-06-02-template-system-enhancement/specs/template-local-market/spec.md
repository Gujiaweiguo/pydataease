## ADDED Requirements

### Requirement: Template market reads from local database
The `TemplateMarketService` SHALL query the `visualization_template` table to populate template market content. All returned content items SHALL have `source=manage`.

#### Scenario: Search returns local templates
- **WHEN** `GET /templateMarket/search` is called
- **THEN** the response contains `contents` array where each item is mapped from `visualization_template` records with fields: `id`, `title` (from `name`), `thumbnail` (from `snapshot`), `templateType` (from `dv_type`), `source="manage"`, `classify`, `categoryNames`, and `metas`

#### Scenario: Search with no templates in database
- **WHEN** `GET /templateMarket/search` is called and `visualization_template` has no `node_type=template` records
- **THEN** the response contains `contents: []` and `categories: []`

#### Scenario: Recommend returns latest templates
- **WHEN** `GET /templateMarket/searchRecommend` is called
- **THEN** the response contains at most 8 templates from `visualization_template` ordered by `create_time` descending

### Requirement: Market categories reflect local template categories
`get_categories()` SHALL return category labels derived from `visualization_template_category` records that have associated templates. `get_categories_object()` SHALL include both fixed entries ("最近", "推荐") and database-sourced category entries.

#### Scenario: Categories include database categories
- **WHEN** `GET /templateMarket/categoriesObject` is called and the database has categories "仪表板模板" and "大屏模板" with associated templates
- **THEN** the response includes the fixed entries (`{value:"recent",label:"最近",source:"public"}`, `{value:"suggest",label:"推荐",source:"public"}`) plus entries for each database category with `source="manage"`

#### Scenario: Categories with no database categories
- **WHEN** `GET /templateMarket/categoriesObject` is called and no template categories exist
- **THEN** the response contains only the two fixed entries ("最近", "推荐")

### Requirement: Seed data provides out-of-box templates
The system SHALL provide a seed script (`scripts/seed_template_data.py`) that inserts predefined templates and categories into the database. The script SHALL be idempotent — repeated execution SHALL NOT create duplicate data.

#### Scenario: Seed script creates templates
- **WHEN** `python3 scripts/seed_template_data.py` is executed on an empty database
- **THEN** at least 2 dashboard templates and 2 screen templates are created in `visualization_template`, with corresponding categories in `visualization_template_category` and mappings in `visualization_template_category_map`

#### Scenario: Seed script is idempotent
- **WHEN** `python3 scripts/seed_template_data.py` is executed twice
- **THEN** the number of templates and categories remains the same as after the first execution

### Requirement: Home page template center shows local templates
The workbranch home page "模板中心" section SHALL display templates from `GET /templateMarket/searchRecommend` with their snapshots as thumbnails.

#### Scenario: Home page shows recommended templates
- **WHEN** the workbranch page loads and the database has seeded templates
- **THEN** the template center section displays template cards with snapshot thumbnails and titles

#### Scenario: Home page shows empty state when no templates
- **WHEN** the workbranch page loads and no templates exist
- **THEN** the template center section shows the empty/skeleton state without errors

### Requirement: Template apply uses local template ID
When a user clicks "应用" on a template with `source=manage`, the system SHALL use `newFrom=new_inner_template` and the template's `id` as `templateId`.

#### Scenario: Apply a local template
- **WHEN** user clicks "应用" on a template card from the local market
- **THEN** the system opens the dashboard/screen editor with `createType=template` and `templateId` set to the template's database ID
