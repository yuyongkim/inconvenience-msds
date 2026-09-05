import { qs } from "./lib/dom.js";
import { createToast } from "./components/toast.js";
import { initTabs } from "./pages/tabs.js";
import { initStats } from "./pages/stats.js";
import { initBrowse } from "./pages/browse.js";
import { initConvert } from "./pages/convert.js";
import { initIngredient } from "./pages/ingredient.js";
import { initCatalog } from "./pages/catalog.js";
import { applyStaticText, initLangToggle, onLangChange } from "./lib/i18n.js";

function boot() {
  // Paint the markup in the reader's language before anything else renders.
  applyStaticText();
  initLangToggle(document.querySelector("#lang-toggle"));

  const toast = createToast(qs(document, "#toast"));

  // The catalogue database is 363 MB and the tab is not the landing tab, so
  // its first fetch waits until somebody opens it.
  let catalog = null;
  const tabs = initTabs({
    tabRoot: qs(document, ".tabs"),
    panelRoot: document,
    onTabChange: (name) => {
      if (name === "catalog") catalog?.activate();
    },
  });

  const stats = initStats({ statsEl: qs(document, "#stats-bar") });
  stats.refresh();

  const browse = initBrowse({ root: document, toast });
  const convert = initConvert({ root: document, toast });
  const ingredient = initIngredient({ root: document, toast });
  catalog = initCatalog({ root: document, toast });

  // Views built in JS hold their own copies of the strings, so redraw them when
  // the language changes. The store is untouched; only the rendering repeats.
  onLangChange(() => {
    stats.refresh();
    browse.store.setState({});
    ingredient.renderPresets();
  });

  // Expose tiny hooks for debugging without leaking functions into HTML.
  window.__brailleMsds = {
    tabs,
    stats,
    browse,
    convert,
    ingredient,
    catalog,
  };
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

