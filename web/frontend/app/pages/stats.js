import { apiGet } from "../lib/api.js";

export function initStats({ statsEl }) {
  async function refresh() {
    try {
      const d = await apiGet("/stats");
      statsEl.innerHTML = `
        <div class="stat-item"><strong>${d.total_chemicals.toLocaleString()}</strong> 화학물질</div>
        <div class="stat-item"><strong>${d.total_sections.toLocaleString()}</strong> MSDS 섹션</div>
        <div class="stat-item"><strong>${d.complete_chemicals.toLocaleString()}</strong> 완전(15+)</div>
      `;
    } catch {
      statsEl.innerHTML = "";
    }
  }

  return { refresh };
}

