import { qsa } from "../lib/dom.js";

export function initTabs({ tabRoot, panelRoot, onTabChange }) {
  const tabs = qsa(tabRoot, "[role='tab']");

  function setActive(tabName) {
    for (const t of tabs) {
      const active = t.dataset.tab === tabName;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", active ? "true" : "false");
    }
    for (const p of qsa(panelRoot, ".tab-content")) {
      p.classList.toggle("active", p.id === `tab-${tabName}`);
    }
    onTabChange?.(tabName);
  }

  tabRoot.addEventListener("click", (e) => {
    const btn = e.target.closest("[role='tab']");
    if (!btn) return;
    setActive(btn.dataset.tab);
  });

  tabRoot.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    const idx = tabs.findIndex((t) => t === document.activeElement);
    if (idx === -1) return;
    const next = e.key === "ArrowRight" ? idx + 1 : idx - 1;
    const el = tabs[(next + tabs.length) % tabs.length];
    el.focus();
    setActive(el.dataset.tab);
    e.preventDefault();
  });

  return { setActive };
}

