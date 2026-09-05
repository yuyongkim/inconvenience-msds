import { apiGet, apiUrl } from "../lib/api.js";
import { copyText } from "../lib/clipboard.js";
import { clear, el, qs } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

/**
 * Public-safety catalogues: medicines, pesticides, accident cases.
 *
 * These are four catalogues rather than four tabs. Seven tabs across the top
 * would push the chemical search — the thing people come here for — into a row
 * of competing labels, and the four belong together anyway: they are the same
 * question asked of four registers.
 *
 * The category buttons are built from `/api/catalogs` rather than written here,
 * so a catalogue added to the database appears without a frontend change. That
 * matters more than it looks: the labels are Korean, and a hardcoded list is
 * one that goes stale in a language the maintainer may not be reading closely.
 *
 * There is no cosmetics catalogue and there will not be one on this route. The
 * ingredient dictionary's terms of use prohibit redistribution, so the preview
 * tab — where a visitor pastes their own list — is what is possible.
 */

const PAGE = 30;

export function initCatalog({ root, toast }) {
  const tabsEl = qs(root, "#cat-tabs");
  const searchEl = qs(root, "#cat-search");
  const listEl = qs(root, "#cat-list");
  const countEl = qs(root, "#cat-count");
  const detailEl = qs(root, "#cat-detail");
  const moreBtn = qs(root, "#cat-more");

  let catalogs = [];
  let current = null;
  let offset = 0;
  let total = 0;
  let inflight = null;

  function setBusy(on) {
    listEl.setAttribute("aria-busy", on ? "true" : "false");
  }

  function renderTabs() {
    clear(tabsEl);
    for (const c of catalogs) {
      const btn = el("button", {
        class: "cat-chip" + (c.config === current ? " active" : ""),
        type: "button",
        "aria-pressed": c.config === current ? "true" : "false",
      }, [
        el("span", { class: "cat-chip-label", text: c.label }),
        el("span", { class: "cat-chip-count", text: c.records.toLocaleString() }),
      ]);
      btn.addEventListener("click", () => select(c.config));
      tabsEl.appendChild(btn);
    }
  }

  function renderRows(rows, append) {
    if (!append) clear(listEl);
    if (!rows.length && !append) {
      listEl.appendChild(el("p", { class: "list-empty", text: t("cat.none") }));
      return;
    }
    for (const r of rows) {
      const item = el("button", {
        class: "cat-item",
        type: "button",
        "data-id": r.record_id,
      }, [
        el("span", { class: "cat-item-name", text: r.name }),
        el("span", { class: "cat-item-size", text: `${r.text_chars.toLocaleString()}자` }),
      ]);
      item.addEventListener("click", () => open(r.record_id, item));
      listEl.appendChild(item);
    }
  }

  async function load({ append = false } = {}) {
    if (!current) return;
    if (inflight) inflight.abort();
    const ctrl = new AbortController();
    inflight = ctrl;
    setBusy(true);
    try {
      const q = encodeURIComponent(searchEl.value.trim());
      const d = await apiGet(
        `/catalog/${current}?limit=${PAGE}&offset=${offset}&search=${q}`,
        { signal: ctrl.signal });
      total = d.total;
      countEl.textContent = t("cat.count", { n: total.toLocaleString(), unit: d.unit });
      renderRows(d.results, append);
      moreBtn.hidden = offset + d.results.length >= total;
    } catch (err) {
      if (err.name !== "AbortError") {
        clear(listEl);
        listEl.appendChild(el("p", { class: "error-box", text: t("cat.failed") }));
      }
    } finally {
      if (inflight === ctrl) inflight = null;
      setBusy(false);
    }
  }

  async function open(recordId, item) {
    for (const other of listEl.querySelectorAll(".cat-item.active")) {
      other.classList.remove("active");
    }
    if (item) item.classList.add("active");

    clear(detailEl);
    detailEl.appendChild(el("p", { class: "skeleton", text: t("cat.loading") }));
    try {
      const d = await apiGet(`/catalog/${current}/${encodeURIComponent(recordId)}`);
      clear(detailEl);
      detailEl.appendChild(el("h3", { class: "cat-title", text: d.name }));
      detailEl.appendChild(el("p", {
        class: "cat-stats",
        text: t("cat.stats", {
          chars: d.stats.text_chars.toLocaleString(),
          cells: d.stats.braille_cells.toLocaleString(),
          ratio: d.stats.expansion_ratio.toFixed(2),
        }),
      }));

      const actions = el("div", { class: "cat-actions" });
      const copy = el("button", { class: "btn", type: "button", text: t("cat.copy") });
      copy.addEventListener("click", async () => {
        await copyText(d.braille);
        toast(t("cat.copied"));
      });
      actions.appendChild(copy);
      for (const [ext, key] of [["txt", "cat.txt"], ["brf", "cat.brf"]]) {
        actions.appendChild(el("a", {
          class: "btn",
          href: apiUrl(`/catalog/${current}/${encodeURIComponent(recordId)}/braille.${ext}`),
          text: t(key),
        }));
      }
      detailEl.appendChild(actions);

      // Sections in reading order, each with its braille beneath. The order is
      // the adapter's decision and the reason this is not just a text dump.
      for (const s of d.sections) {
        const box = el("div", { class: "cat-section" });
        if (s.title) box.appendChild(el("h4", { text: s.title }));
        box.appendChild(el("p", { class: "cat-korean", text: s.korean }));
        box.appendChild(el("p", { class: "braille-text", text: s.braille }));
        detailEl.appendChild(box);
      }
    } catch {
      clear(detailEl);
      detailEl.appendChild(el("p", { class: "error-box", text: t("cat.failed") }));
    }
  }

  function select(config) {
    current = config;
    offset = 0;
    clear(detailEl);
    detailEl.appendChild(el("p", { class: "empty-detail", text: t("cat.pick") }));
    renderTabs();
    load();
  }

  let timer = null;
  searchEl.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => { offset = 0; load(); }, 250);
  });

  moreBtn.addEventListener("click", () => {
    offset += PAGE;
    load({ append: true });
  });

  return {
    async activate() {
      if (catalogs.length) return;
      try {
        const d = await apiGet("/catalogs");
        catalogs = d.catalogs || [];
        if (!catalogs.length) {
          tabsEl.appendChild(el("p", { class: "list-empty", text: t("cat.unbuilt") }));
          return;
        }
        select(catalogs[0].config);
      } catch {
        clear(tabsEl);
        tabsEl.appendChild(el("p", { class: "error-box", text: t("cat.unbuilt") }));
      }
    },
  };
}
