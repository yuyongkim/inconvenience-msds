import { apiGet } from "../lib/api.js";
import { clear, el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

export function initStats({ statsEl }) {
  async function refresh() {
    try {
      const d = await apiGet("/stats");
      clear(statsEl);
      statsEl.appendChild(
        el("div", { class: "stat-item" }, [el("strong", { text: d.total_chemicals.toLocaleString() }), t("stats.chemicals")]),
      );
      statsEl.appendChild(
        el("div", { class: "stat-item" }, [el("strong", { text: d.total_sections.toLocaleString() }), t("stats.sections")]),
      );
      statsEl.appendChild(
        el("div", { class: "stat-item" }, [el("strong", { text: d.complete_chemicals.toLocaleString() }), t("stats.complete")]),
      );
    } catch {
      statsEl.innerHTML = "";
    }
  }

  return { refresh };
}
