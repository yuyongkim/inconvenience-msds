import { apiGet } from "../lib/api.js";
import { clear, el, escapeHtml, qs } from "../lib/dom.js";

function renderListSkeleton() {
  return `
    <div class="list-header">불러오는 중</div>
    <div class="skeleton">
      <div class="skeleton-row"></div>
      <div class="skeleton-row"></div>
      <div class="skeleton-row"></div>
    </div>
  `;
}

function renderDetailSkeleton() {
  return `
    <div class="skeleton">
      <div class="skeleton-row" style="width: 48%"></div>
      <div class="skeleton-row" style="width: 86%"></div>
      <div class="skeleton-row" style="width: 72%"></div>
    </div>
  `;
}

function renderError({ title, message, actionLabel }) {
  const box = el("div", { class: "error-box", role: "alert" }, [
    el("strong", { text: title }),
    el("div", { text: message }),
  ]);
  if (actionLabel) {
    box.appendChild(
      el("div", { class: "empty-actions" }, [
        el("button", { class: "btn btn-secondary", type: "button", "data-action": "retry" }, [actionLabel]),
      ]),
    );
  }
  return box;
}

function renderEmptyDetail({ onFocusSearch, onRandomPick }) {
  return el("div", { class: "placeholder" }, [
    el("div", { class: "empty-state" }, [
      el("div", { class: "empty-copy" }, [
        el("h3", { text: "왼쪽 목록에서 화학물질을 선택하세요" }),
        el("p", {
          text:
            "검색하거나 목록을 클릭하면 MSDS 전문이 점자로 변환됩니다. 변환 결과는 섹션별로 한국어/점자를 나란히 확인할 수 있습니다.",
        }),
        el("div", { class: "empty-actions" }, [
          el("button", { class: "btn btn-secondary", type: "button" }, ["검색창으로 이동"]),
          el("button", { class: "btn btn-secondary", type: "button" }, ["목록에서 임의 선택"]),
        ]),
      ]),
      el("div", { class: "empty-preview" }, [
        el("div", { class: "braille-hero", html: "&#x2803;&#x2817;&#x2807;" }),
        el("div", { class: "sub", text: "선택 후 다운로드 버튼에서 Unicode TXT / BRF를 내려받을 수 있습니다." }),
      ]),
    ]),
  ]);
}

export function initBrowse({ root, toast }) {
  const listEl = qs(root, "#list");
  const detailEl = qs(root, "#detail");
  const searchForm = qs(root, "#search-form");
  const searchInput = qs(root, "#search-input");
  const clearBtn = qs(root, "#search-clear");

  let inflightList = null;
  let inflightDetail = null;
  let currentChemId = null;

  function focusSearch() {
    searchInput.focus();
    searchInput.select();
  }

  function loadRandomFromList() {
    const items = Array.from(listEl.querySelectorAll("button.list-item[data-chem-id]"));
    if (items.length === 0) return;
    const idx = Math.floor(Math.random() * items.length);
    const chemId = items[idx].dataset.chemId;
    if (chemId) loadDetail(chemId);
  }

  function setEmptyDetail() {
    clear(detailEl);
    const node = renderEmptyDetail({ onFocusSearch: focusSearch, onRandomPick: loadRandomFromList });
    detailEl.appendChild(node);
    const actions = node.querySelectorAll(".empty-actions button");
    actions[0]?.addEventListener("click", focusSearch);
    actions[1]?.addEventListener("click", loadRandomFromList);
  }

  async function loadList(query = "") {
    listEl.innerHTML = renderListSkeleton();

    if (inflightList) inflightList.abort();
    inflightList = new AbortController();
    const { signal } = inflightList;

    try {
      const d = await apiGet(`/chemicals?limit=100${query ? `&search=${encodeURIComponent(query)}` : ""}`, { signal });
      if (!d.results || d.results.length === 0) {
        listEl.innerHTML = `
          <div class="list-header">결과 없음</div>
          <div class="loader">다른 키워드로 다시 검색해 보세요</div>
        `;
        return;
      }

      listEl.innerHTML =
        `<div class="list-header">${d.total.toLocaleString()}개 중 ${d.results.length}개 표시</div>` +
        d.results
          .map(
            (c) => `
              <button class="list-item" type="button" data-chem-id="${escapeHtml(c.chem_id)}">
                <div class="chem-id">${escapeHtml(c.chem_id)}</div>
                <div class="chem-name">${escapeHtml(c.name)}</div>
              </button>
            `,
          )
          .join("");
    } catch (e) {
      if (e.name === "AbortError") return;
      clear(listEl);
      listEl.appendChild(
        renderError({
          title: "목록을 불러오지 못했습니다",
          message: "서버 연결을 확인한 뒤 다시 시도하세요.",
          actionLabel: "다시 시도",
        }),
      );
    }
  }

  async function loadDetail(chemId) {
    currentChemId = chemId;
    for (const btn of listEl.querySelectorAll("button.list-item[data-chem-id]")) {
      btn.classList.toggle("active", btn.dataset.chemId === chemId);
    }

    detailEl.innerHTML = renderDetailSkeleton();

    if (inflightDetail) inflightDetail.abort();
    inflightDetail = new AbortController();
    const { signal } = inflightDetail;

    try {
      const d = await apiGet(`/chemicals/${encodeURIComponent(chemId)}/braille`, { signal });

      const ratio =
        d?.stats?.korean_chars > 0 ? (d.stats.braille_cells / d.stats.korean_chars).toFixed(2) : "—";

      let html = `
        <div class="detail-header">
          <h2>${escapeHtml(d.name)}</h2>
          <div class="detail-meta">
            <span class="meta-chip">ID ${escapeHtml(d.chem_id)}</span>
            <span class="meta-chip">한국어 ${Number(d.stats.korean_chars).toLocaleString()}자</span>
            <span class="meta-chip">점자 ${Number(d.stats.braille_cells).toLocaleString()}셀</span>
            <span class="meta-chip">비율 ${ratio}x</span>
          </div>
        </div>
        <div class="download-row">
          <a href="/api/chemicals/${encodeURIComponent(chemId)}/braille.txt" download class="btn btn-primary">Unicode TXT</a>
          <a href="/api/chemicals/${encodeURIComponent(chemId)}/braille.brf" download class="btn btn-secondary">BRF (엠보서)</a>
        </div>
        <div class="detail-body">
      `;

      for (const sec of d.sections ?? []) {
        html += `
          <div class="section">
            <div class="section-title" role="button" tabindex="0" data-action="toggle-section">
              <span>${escapeHtml(sec.section_no)}. ${escapeHtml(sec.title)}</span>
              <span class="toggle">접기/펼치기</span>
            </div>
            <div class="section-content">
              <div class="section-korean">
                <div class="col-label">한국어</div>
                ${escapeHtml(sec.korean)}
              </div>
              <div class="section-braille">
                <div class="col-label">점자</div>
                ${escapeHtml(sec.braille)}
              </div>
            </div>
          </div>
        `;
      }

      html += "</div>";
      detailEl.innerHTML = html;
    } catch (e) {
      if (e.name === "AbortError") return;
      clear(detailEl);
      detailEl.appendChild(
        renderError({
          title: "상세 정보를 불러오지 못했습니다",
          message: "서버 연결을 확인한 뒤 다시 시도하세요.",
          actionLabel: "다시 시도",
        }),
      );
    }
  }

  function onSearchSubmit() {
    const q = searchInput.value.trim();
    loadList(q);
  }

  function clearSearch() {
    searchInput.value = "";
    loadList("");
    toast.show("검색 조건이 초기화되었습니다");
    focusSearch();
  }

  // Events
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    onSearchSubmit();
  });
  clearBtn.addEventListener("click", clearSearch);

  listEl.addEventListener("click", (e) => {
    const btn = e.target.closest("button.list-item[data-chem-id]");
    if (!btn) return;
    loadDetail(btn.dataset.chemId);
  });

  listEl.addEventListener("click", (e) => {
    const action = e.target.closest("[data-action='retry']");
    if (!action) return;
    const q = searchInput.value.trim();
    loadList(q);
  });

  detailEl.addEventListener("click", (e) => {
    const retry = e.target.closest("[data-action='retry']");
    if (retry) {
      if (currentChemId) loadDetail(currentChemId);
      return;
    }
    const title = e.target.closest("[data-action='toggle-section']");
    if (!title) return;
    const content = title.nextElementSibling;
    if (!content) return;
    content.classList.toggle("collapsed");
  });

  detailEl.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const title = e.target.closest("[data-action='toggle-section']");
    if (!title) return;
    title.click();
    e.preventDefault();
  });

  // Init
  setEmptyDetail();
  loadList("");

  return {
    focusSearch,
    loadRandomFromList,
    loadList,
    loadDetail,
  };
}

