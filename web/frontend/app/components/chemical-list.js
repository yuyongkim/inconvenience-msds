import { clear, el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

function renderListHeader(total, shown) {
  return el("div", {
    class: "list-header",
    text: t("list.shown", { total: total.toLocaleString(), shown: shown.toLocaleString() }),
  });
}

export function renderChemicalList({ listEl, chemicals, total, selectedChemIds = [] }) {
  clear(listEl);
  listEl.appendChild(renderListHeader(total, chemicals.length));
  const selectedSet = new Set(selectedChemIds);
  for (const c of chemicals) {
    const row = el("div", { class: "list-row", "data-chem-id": c.chem_id }, [
      el("label", { class: "list-check" }, [
        el("input", {
          type: "checkbox",
          "data-select-chem-id": c.chem_id,
          checked: selectedSet.has(c.chem_id) ? "checked" : null,
        }),
      ]),
      el("button", { class: "list-item", type: "button", "data-chem-id": c.chem_id }, [
        el("div", { class: "chem-id", text: c.chem_id }),
        el("div", { class: "chem-name", text: c.name }),
      ]),
    ]);
    listEl.appendChild(row);
  }
}

export function setListSelection({ listEl, chemId }) {
  for (const row of listEl.querySelectorAll(".list-row[data-chem-id]")) {
    row.classList.toggle("active", row.dataset.chemId === chemId);
  }
}
