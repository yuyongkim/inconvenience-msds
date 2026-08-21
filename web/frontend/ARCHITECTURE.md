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

Bulk export follows the same split:

1. Browse page collects selected `chem_id`s and chosen formats.
2. Frontend creates a `POST /api/bulk-jobs` request.
3. The page polls `GET /api/bulk-jobs/{job_id}` until completion.
4. The finished ZIP is downloaded from `GET /api/bulk-jobs/{job_id}/download`.

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
- Persisted bulk-job history so completed ZIPs survive reloads and can be resumed.

## Guardrails

- No framework migration unless the cost is justified by features that native modules cannot support.
- No inline event handlers in HTML.
- No component should directly mutate unrelated DOM outside its mount root.
- Keep backend API contracts narrow and explicit. Frontend expansion should not require scraping HTML responses.

## Language

`app/lib/i18n.js` holds every UI string in Korean and English. Markup carries
`data-i18n` / `data-i18n-placeholder` / `data-i18n-label` attributes; views built
in JS call `t(key, params)`.

The toggle in the header writes the choice to `localStorage` and sets
`document.documentElement.lang`. That attribute matters more than usual here:
screen readers choose their voice from it, so showing English under `lang="ko"`
would have the page read aloud in a Korean voice.

`onLangChange` redraws the JS-rendered views. The store is not touched — only the
rendering repeats.

The corpus and the MSDS text stay Korean. This covers the interface only, so that
a reader who cannot read Korean can still reach the data and the download formats.
