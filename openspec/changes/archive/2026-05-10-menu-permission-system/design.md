## Context

The frontend (`permission.ts` router guard) calls `GET /menu/query` on first navigation after login. The response must be a tree of MenuVO objects that the frontend converts into Vue Router routes via `generateRoutesFn2()`. The Java backend stores menus in `core_menu` table (id, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth) and builds a tree by grouping rows by `pid`.

## Goals / Non-Goals

**Goals:**
- Return a valid menu tree from `GET /de2api/menu/query` that renders the DataEase sidebar
- Include core community menus: workbranch, panel, screen, data (dataset+datasource), system settings
- Match the Java `MenuVO` response shape exactly

**Non-Goals:**
- Fine-grained permission filtering (xpack enterprise feature)
- Menu CRUD operations (add/edit/delete menus)
- Role-based menu visibility

## Decisions

### D1: Hardcoded community menu seed in Alembic migration
**Decision**: Seed all community menu items in the Alembic migration, matching Java's `V2.0__core_ddl.sql` seed data.
**Rationale**: Simple, reproducible, matches Java baseline. No need for runtime menu management in community edition.

### D2: Tree building via pid grouping
**Decision**: Load all menu rows, group by pid, recursively build tree. Same algorithm as Java `buildPOTree()`.
**Rationale**: Simple, proven approach. Only ~20 rows, no performance concern.

### D3: All menus visible to all authenticated users
**Decision**: Community edition shows all menus to every authenticated user. No permission filtering.
**Rationale**: Permission filtering is an xpack enterprise feature. Community edition has no role system.

## Risks / Trade-offs

- **[Menu i18n]**: Java resolves titles via `Translator.get("i18n_menu." + name)`. Python will return the i18n key and let frontend handle it — **actually Java returns resolved titles, so we need to do the same or the frontend shows raw keys** → Mitigation: Return resolved Chinese titles in `meta.title` for now
