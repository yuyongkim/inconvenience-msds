import { apiGet, apiPostJson } from "../lib/api.js";
import { copyText } from "../lib/clipboard.js";
import { clear, el, qs } from "../lib/dom.js";
import { getLang, t } from "../lib/i18n.js";

/**
 * Ingredient list preview.
 *
 * The rest of the site answers "what does this chemical's MSDS say in braille".
 * This tab answers a different question: what a cosmetics label, which has no
 * room for braille, sounds like once it has been given some structure.
 *
 * The presets exist because a visitor almost never has an ingredient list to
 * paste. Without something to press, the tab reads as a form to fill in and
 * nobody fills it in.
 */

const BAND_KEYS = {
  most: "ing.band.most",
  high: "ing.band.high",
  middle: "ing.band.middle",
  trace: "ing.band.trace",
};

export function initIngredient({ root, toast }) {
  const presetsEl = qs(root, "#ing-presets");
  const inputEl = qs(root, "#ing-input");
  const summaryEl = qs(root, "#ing-summary");
  const resultEl = qs(root, "#ing-result");
  const runBtn = qs(root, "#ing-run");
  const copyBtn = qs(root, "#ing-copy");
  const clearBtn = qs(root, "#ing-clear");

  let presets = [];
  let braille = "";

  function renderPresets() {
    clear(presetsEl);
    for (const p of presets) {
      const btn = el("button", {
        class: "ing-preset",
        type: "button",
        text: getLang() === "en" ? p.label_en : p.label_ko,
      });
      btn.addEventListener("click", () => {
        inputEl.value = p.text;
        run();
      });
      presetsEl.appendChild(btn);
    }
  }

  async function loadPresets() {
    try {
      const d = await apiGet("/ingredient-presets");
      presets = d.presets || [];
      renderPresets();
    } catch {
      // A failed preset fetch leaves the textarea, which still works.
      clear(presetsEl);
    }
  }

  function renderResult(d) {
    clear(resultEl);

    const allergens = el("div", { class: "ing-block" });
    allergens.appendChild(el("div", { class: "ing-block-title", text: t("ing.allergensTitle") }));
    if (d.allergens.length) {
      const list = el("ul", { class: "ing-allergens" });
      for (const a of d.allergens) {
        const li = el("li");
        li.appendChild(el("strong", { text: a.name }));
        if (a.english) li.appendChild(el("span", { class: "ing-en", text: a.english }));
        list.appendChild(li);
      }
      allergens.appendChild(list);
      allergens.appendChild(el("p", { class: "ing-note", text: t("ing.allergensNote") }));
    } else {
      allergens.appendChild(el("p", { class: "ing-note", text: t("ing.allergensNone") }));
    }
    resultEl.appendChild(allergens);

    const table = el("table", { class: "ing-table" });
    const thead = el("thead");
    const head = el("tr");
    for (const k of ["ing.col.no", "ing.col.name", "ing.col.band", "ing.col.roots"]) {
      head.appendChild(el("th", { scope: "col", text: t(k) }));
    }
    thead.appendChild(head);
    table.appendChild(thead);
    const tbody = el("tbody");
    table.appendChild(tbody);
    for (const i of d.ingredients) {
      const tr = el("tr", { class: i.allergen ? "is-allergen" : "" });
      tr.appendChild(el("td", { text: String(i.position) }));
      const nameTd = el("td");
      nameTd.appendChild(el("span", { text: i.name }));
      if (i.allergen) nameTd.appendChild(el("span", { class: "ing-flag", text: t("ing.flag") }));
      tr.appendChild(nameTd);
      tr.appendChild(el("td", { text: t(BAND_KEYS[i.band] || "ing.band.trace") }));
      tr.appendChild(el("td", { class: "ing-roots", text: i.roots.join(", ") || "—" }));
      tbody.appendChild(tr);
    }

    const tableBlock = el("div", { class: "ing-block" });
    tableBlock.appendChild(el("div", { class: "ing-block-title", text: t("ing.tableTitle") }));
    const scroller = el("div", { class: "ing-table-wrap" });
    scroller.appendChild(table);
    tableBlock.appendChild(scroller);
    resultEl.appendChild(tableBlock);

    const brailleBlock = el("div", { class: "ing-block" });
    brailleBlock.appendChild(
      el("div", {
        class: "ing-block-title",
        text: t("ing.brailleTitle", { n: d.braille_cells.toLocaleString() }),
      })
    );
    brailleBlock.appendChild(el("div", { class: "convert-output", text: d.braille }));
    resultEl.appendChild(brailleBlock);
  }

  async function run() {
    const text = inputEl.value.trim();
    if (!text) return;
    summaryEl.textContent = t("ing.running");
    clear(resultEl);
    try {
      const d = await apiPostJson("/ingredient-summary", { text });
      braille = d.braille;
      summaryEl.textContent = d.summary;
      renderResult(d);
    } catch {
      braille = "";
      summaryEl.textContent = t("ing.failed");
    }
  }

  async function copyBraille() {
    if (!braille) return;
    const r = await copyText(braille);
    toast.show(r.ok ? t("convert.copied") : t("convert.copyFailed"));
  }

  function reset() {
    inputEl.value = "";
    braille = "";
    summaryEl.textContent = "";
    clear(resultEl);
  }

  runBtn.addEventListener("click", run);
  copyBtn.addEventListener("click", copyBraille);
  clearBtn.addEventListener("click", reset);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.ctrlKey) run();
  });

  loadPresets();

  return { run, reset, renderPresets };
}
