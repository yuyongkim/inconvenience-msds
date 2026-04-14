import { qs } from "./lib/dom.js";
import { createToast } from "./components/toast.js";
import { initTabs } from "./pages/tabs.js";
import { initStats } from "./pages/stats.js";
import { initBrowse } from "./pages/browse.js";
import { initConvert } from "./pages/convert.js";

function boot() {
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

