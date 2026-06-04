## 1. Template Market Card — Download Button

- [x] 1.1 Add download icon button to `TemplateMarketV2Item.vue` hover area (alongside preview/apply), emit `templateDownload` event with the template object
- [x] 1.2 In `index.vue` `full` view, handle `templateDownload` event: call `exportTemplate(id)` API, save response as `.DET2` file via FileSaver
- [x] 1.3 Import and register `exportTemplate` from `@/api/template` in `index.vue`

## 2. Template Market Card — Delete Button

- [x] 2.1 Add delete icon button to `TemplateMarketV2Item.vue` hover area, emit `templateDelete` event with the template object
- [x] 2.2 In `index.vue` `full` view, handle `templateDelete` event: show `ElMessageBox.confirm` dialog, on confirm call `templateDelete(id, categoryId)` API
- [x] 2.3 After successful deletion, call `initMarketTemplate` to refresh the template list preserving current filters

## 3. Template Market Toolbar — Upload Button

- [x] 3.1 Replace "open import entry" button in `index.vue` toolbar with "upload template" button
- [x] 3.2 Import `DeTemplateImport` component from `views/template/component/DeTemplateImport.vue` and add it to the `index.vue` template
- [x] 3.3 Wire upload button click to open `DeTemplateImport` dialog
- [x] 3.4 On successful import completion, close dialog and call `initMarketTemplate` to refresh the template list

## 4. Gate Scope — CRUD limited to full view

- [x] 4.1 Verify download/delete buttons only render in `full` view mode (not in `marketPreview` or `createPreview`)
- [x] 4.2 Verify upload button only renders in `full` view mode toolbar

## 5. Verification

- [x] 5.1 Run `npm run ts:check` — zero type errors in changed files
- [x] 5.2 Run `npm run lint` — zero new lint errors
- [x] 5.3 Run `npm run lint:stylelint` — zero new style errors
- [x] 5.4 Manual QA in browser: page loads with 0 errors, import button visible in toolbar, download/delete icons visible on template cards
