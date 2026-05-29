## ADDED Requirements

### Requirement: Element-plus plugin tests
The test suite SHALL verify that the element-plus setup functions correctly register plugins, components, and icons on the Vue app.

#### Scenario: setupElementPlus registers ElLoading plugin
- **WHEN** `setupElementPlus(app)` is called
- **THEN** `app.use(ElLoading)` SHALL be called

#### Scenario: setupElementPlus registers ElScrollbar component
- **WHEN** `setupElementPlus(app)` is called
- **THEN** `app.component('ElScrollbar', ...)` SHALL be called

#### Scenario: setupElementPlusIcons registers all icons
- **WHEN** `setupElementPlusIcons(app)` is called
- **THEN** each icon from `@element-plus/icons-vue` SHALL be registered via `app.component(key, component)`

#### Scenario: setElementPlusLocale sets locale on ElConfigProvider
- **WHEN** `setElementPlusLocale(localeObj)` is called
- **THEN** `ElConfigProvider.locale` SHALL be set to `localeObj`

### Requirement: Vue-i18n plugin tests
The test suite SHALL verify the vue-i18n plugin setup, mocking the locale store and axios service dependencies.

#### Scenario: setupI18n calls app.use with i18n instance
- **WHEN** `setupI18n(app)` completes
- **THEN** `app.use()` SHALL be called with the created i18n instance

#### Scenario: setupI18n creates i18n with correct options
- **WHEN** `setupI18n(app)` completes
- **THEN** the i18n instance SHALL have `legacy: false` and `locale` matching the locale store

#### Scenario: createI18nOptions returns correct structure
- **WHEN** `createI18nOptions` is called with a mocked locale store returning lang `zh-CN`
- **THEN** the returned options SHALL include `locale: 'zh-CN'` and a `messages` object with `zh-CN` key
