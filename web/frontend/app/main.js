import { qs } from "./lib/dom.js";
import { createToast } from "./components/toast.js";
import { initTabs } from "./pages/tabs.js";
import { initStats } from "./pages/stats.js";
import { initBrowse } from "./pages/browse.js";
import { initConvert } from "./pages/convert.js";
import { applyStaticText, initLangToggle, onLangChange } from "./lib/i18n.js";

function boot() {
  // Paint the markup in the reader's language before anything else renders.
  applyStaticText();
  initLangToggle(document.querySelector("#lang-toggle"));

  const toast = createToast(qs(document, "#toast"));

  const tabs = initTabs({
    tabRoot: qs(document, ".tabs"),
    panelRoot: document,
    onTabChange: () => {},
  });

  const stats = initStats({ statsEl: qs(document, "#stats-bar") });
  stats.refresh();

  const browse = initBrowse({ root: document, toast });
  const convert = initConvert({ root: document, toast });

  // Views built in JS hold their own copies of the strings, so redraw them when
  // the language changes. The store is untouched; only the rendering repeats.
  onLangChange(() => {
    stats.refresh();
    browse.store.setState({});
  });

  // Expose tiny hooks for debugging without leaking functions into HTML.
  window.__brailleMsds = {
    tabs,
    stats,
    browse,
    convert,
  };
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

