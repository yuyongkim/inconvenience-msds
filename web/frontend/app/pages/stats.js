import { apiGet } from "../lib/api.js";
import { clear, el } from "../lib/dom.js";

export function initStats({ statsEl }) {
  async function refresh() {
    try {
      const d = await apiGet("/stats");
      clear(statsEl);
      statsEl.appendChild(
        el("div", { class: "stat-item" }, [el("strong", { text: d.total_chemicals.toLocaleString() }), " 화학물질"]),
      );
      statsEl.appendChild(
        el("div", { class: "stat-item" }, [el("strong", { text: d.total_sections.toLocaleString() }), " MSDS 섹션"]),
      );
      statsEl.appendChild(
        el("div", { class: "stat-item" }, [el("strong", { text: d.complete_chemicals.toLocaleString() }), " 완전(15+)"]),
      );
    } catch {
      statsEl.innerHTML = "";
    }
  }

  return { refresh };
}
