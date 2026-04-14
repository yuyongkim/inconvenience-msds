import { clear, el } from "../lib/dom.js";

function renderListHeader(total, shown) {
  return el("div", { class: "list-header", text: `${total.toLocaleString()}개 중 ${shown.toLocaleString()}개 표시` });
}

export function renderChemicalList({ listEl, chemicals, total }) {
  clear(listEl);
  listEl.appendChild(renderListHeader(total, chemicals.length));
  for (const c of chemicals) {
    const btn = el("button", { class: "list-item", type: "button", "data-chem-id": c.chem_id }, [
      el("div", { class: "chem-id", text: c.chem_id }),
      el("div", { class: "chem-name", text: c.name }),
    ]);
    listEl.appendChild(btn);
  }
}

export function setListSelection({ listEl, chemId }) {
  for (const btn of listEl.querySelectorAll("button.list-item[data-chem-id]")) {
    btn.classList.toggle("active", btn.dataset.chemId === chemId);
  }
}

