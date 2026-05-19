## 1. Router Tests

- [ ] 1.1 Create `src/router/__tests__/index.test.ts` — test route configuration: hash history mode, static route paths (/login, /admin-login, /401, /workbranch, etc.), setupRouter calls app.use()
- [ ] 1.2 Create `src/permission/__tests__/index.test.ts` — test navigation guard in `src/permission.ts`: whitelist (/login, /de-link/*, /chart-view, /admin-login, /401), redirect to login without token, authenticated login → workbranch redirect, embedded token routes
- [ ] 1.3 Create `src/router/__tests__/establish.test.ts` — test route generation utilities: generateRoutesFn2 resolves Layout/view components, formatRoute flattens single-child routes, resolvePath resolves nested paths

## 2. Directive Tests

- [ ] 2.1 Create `src/directive/__tests__/Permission.test.ts` — mock interactiveStore, test checkPermission: element kept when all permissions pass (every), element removed when any fails, non-array throws error, flags map to panel/screen/dataset/datasource
- [ ] 2.2 Create `src/directive/__tests__/ClickOutside.test.ts` — test vClickOutside: click outside triggers callback, click inside does not, beforeMount adds listener, unmounted removes listener
- [ ] 2.3 Create `src/directive/__tests__/index.test.ts` — test installDirective: registers 'permission' and 'click-outside' directives on app

## 3. Plugin Tests

- [ ] 3.1 Create `src/plugins/__tests__/element-plus.test.ts` — mock element-plus-secondary and @element-plus/icons-vue, test setupElementPlus registers ElLoading + ElScrollbar, setupElementPlusIcons registers all icons, setElementPlusLocale sets ElConfigProvider.locale
- [ ] 3.2 Create `src/plugins/__tests__/vue-i18n.test.ts` — mock @/store/modules/locale, @/config/axios/service, test setupI18n calls app.use with i18n, creates i18n with legacy:false, locale matches store

## 4. Final Verification

- [ ] 4.1 Run `npx vitest run` — all new tests pass, total count increased from 1445
- [ ] 4.2 Run `npm run lint` — zero lint errors in new test files
