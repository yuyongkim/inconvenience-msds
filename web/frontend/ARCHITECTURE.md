# Frontend Architecture

This frontend stays deliberately buildless. The backend serves static files from `web/frontend/`, and the browser runs native ES modules directly.

## Structure

- `index.html`
  Thin document shell. Only static markup and module entry references live here.
- `app.css`
  Shared visual system and layout rules.
- `app/main.js`
  Bootstraps the app and wires pages together.
- `app/lib/`
  Small generic utilities. Keep these framework-agnostic.
- `app/state/`
  Shared store primitives and feature state containers.
- `app/components/`
  Pure DOM renderers. These should not fetch data or own business rules.
- `app/pages/`
  Page controllers. They bind DOM events, call APIs, update stores, and select components to render.

## Current Data Flow

1. `main.js` boots tabs, stats, browse, and convert.
2. `pages/*` call `lib/api.js` for network requests.
3. Page controllers update state in `app/state/*`.
4. Store subscribers trigger component rendering into the DOM.

This split matters because future features should be able to change one layer without rewriting the others.

## Extension Rules

When adding a new feature:

1. Add shared state to `app/state/` if the feature has more than one UI state.
2. Add reusable DOM renderers to `app/components/` if markup will be reused or has multiple visual states.
3. Keep request code in `lib/api.js` or a nearby feature-specific helper, not inside components.
4. Keep text rendering on `textContent` / DOM nodes for safety. Avoid reintroducing large `innerHTML` blocks for data payloads.
5. Keep `index.html` stable. New behavior should usually only require adding DOM anchors plus a module import.

## Good Next Expansions

- Search pagination and virtualized list rendering for the full 48k dataset.
- Section filters, favorites, and recent-history on top of `browse-store`.
- Route-level deep links such as `?chem_id=000001&tab=convert`.
- A second browse source, for example local sample DB vs full DB, behind a source selector in store state.
- Download job queue / progress states if BRF or PDF generation becomes asynchronous.

## Guardrails

- No framework migration unless the cost is justified by features that native modules cannot support.
- No inline event handlers in HTML.
- No component should directly mutate unrelated DOM outside its mount root.
- Keep backend API contracts narrow and explicit. Frontend expansion should not require scraping HTML responses.

