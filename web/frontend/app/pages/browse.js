import { apiGet } from "../lib/api.js";
import { clear, qs } from "../lib/dom.js";
import { renderListSkeleton, renderDetailSkeleton } from "../components/skeleton.js";
import { renderErrorBox } from "../components/error-box.js";
import { renderEmptyDetail } from "../components/empty-detail.js";
import { renderChemicalList, setListSelection } from "../components/chemical-list.js";
import { renderChemicalDetail } from "../components/chemical-detail.js";

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
    detailEl.appendChild(renderEmptyDetail());
  }

  async function loadList(query = "") {
    clear(listEl);
    listEl.appendChild(renderListSkeleton());

    if (inflightList) inflightList.abort();
    inflightList = new AbortController();
    const { signal } = inflightList;

    try {
      const d = await apiGet(`/chemicals?limit=100${query ? `&search=${encodeURIComponent(query)}` : ""}`, { signal });
      if (!d.results || d.results.length === 0) {
        clear(listEl);
        listEl.appendChild(
          Object.assign(document.createElement("div"), {
            className: "list-header",
            textContent: "결과 없음",
          }),
        );
        listEl.appendChild(
          Object.assign(document.createElement("div"), {
            className: "loader",
            textContent: "다른 키워드로 다시 검색해 보세요",
          }),
        );
        return;
      }
      renderChemicalList({ listEl, chemicals: d.results, total: d.total });
    } catch (e) {
      if (e.name === "AbortError") return;
      clear(listEl);
      listEl.appendChild(
        renderErrorBox({
          title: "목록을 불러오지 못했습니다",
          message: "서버 연결을 확인한 뒤 다시 시도하세요.",
          actionLabel: "다시 시도",
        }),
      );
    }
  }

  async function loadDetail(chemId) {
    currentChemId = chemId;
    setListSelection({ listEl, chemId });
    clear(detailEl);
    detailEl.appendChild(renderDetailSkeleton());

    if (inflightDetail) inflightDetail.abort();
    inflightDetail = new AbortController();
    const { signal } = inflightDetail;

    try {
      const d = await apiGet(`/chemicals/${encodeURIComponent(chemId)}/braille`, { signal });
      renderChemicalDetail({ detailEl, chem: d });
    } catch (e) {
      if (e.name === "AbortError") return;
      clear(detailEl);
      detailEl.appendChild(
        renderErrorBox({
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
    const focus = e.target.closest("[data-action='focus-search']");
    if (focus) {
      focusSearch();
      return;
    }
    const random = e.target.closest("[data-action='random-pick']");
    if (random) {
      loadRandomFromList();
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
