import { apiGet } from "../lib/api.js";
import { clear, qs } from "../lib/dom.js";
import { renderListSkeleton, renderDetailSkeleton } from "../components/skeleton.js";
import { renderErrorBox } from "../components/error-box.js";
import { renderEmptyDetail } from "../components/empty-detail.js";
import { renderListEmpty } from "../components/list-empty.js";
import { renderChemicalList, setListSelection } from "../components/chemical-list.js";
import { renderChemicalDetail } from "../components/chemical-detail.js";
import { createBrowseStore } from "../state/browse-store.js";

export function initBrowse({ root, toast }) {
  const listEl = qs(root, "#list");
  const detailEl = qs(root, "#detail");
  const searchForm = qs(root, "#search-form");
  const searchInput = qs(root, "#search-input");
  const clearBtn = qs(root, "#search-clear");
  const store = createBrowseStore();

  let inflightList = null;
  let inflightDetail = null;

  function focusSearch() {
    searchInput.focus();
    searchInput.select();
  }

  function loadRandomFromList() {
    const items = store.getState().chemicals;
    if (items.length === 0) return;
    const idx = Math.floor(Math.random() * items.length);
    const chemId = items[idx].chem_id;
    if (chemId) loadDetail(chemId);
  }

  function renderList(state) {
    clear(listEl);
    if (state.listStatus === "loading" || state.listStatus === "idle") {
      listEl.appendChild(renderListSkeleton());
      return;
    }
    if (state.listStatus === "error") {
      listEl.appendChild(
        renderErrorBox({
          title: "목록을 불러오지 못했습니다",
          message: state.listError || "서버 연결을 확인한 뒤 다시 시도하세요.",
          actionLabel: "다시 시도",
        }),
      );
      return;
    }
    if (state.listStatus === "empty") {
      listEl.appendChild(renderListEmpty());
      return;
    }

    renderChemicalList({ listEl, chemicals: state.chemicals, total: state.total });
    if (state.currentChemId) {
      setListSelection({ listEl, chemId: state.currentChemId });
    }
  }

  function renderDetail(state) {
    clear(detailEl);
    if (state.detailStatus === "loading") {
      detailEl.appendChild(renderDetailSkeleton());
      return;
    }
    if (state.detailStatus === "error") {
      detailEl.appendChild(
        renderErrorBox({
          title: "상세 정보를 불러오지 못했습니다",
          message: state.detailError || "서버 연결을 확인한 뒤 다시 시도하세요.",
          actionLabel: "다시 시도",
        }),
      );
      return;
    }
    if (state.detailStatus === "ready" && state.detail) {
      renderChemicalDetail({ detailEl, chem: state.detail });
      return;
    }
    detailEl.appendChild(renderEmptyDetail());
  }

  async function loadList(query = "") {
    if (inflightList) inflightList.abort();
    inflightList = new AbortController();
    const { signal } = inflightList;
    store.setState({
      query,
      listStatus: "loading",
      listError: null,
      chemicals: [],
      total: 0,
    });

    try {
      const d = await apiGet(`/chemicals?limit=100${query ? `&search=${encodeURIComponent(query)}` : ""}`, { signal });
      if (!d.results || d.results.length === 0) {
        store.setState({
          listStatus: "empty",
          chemicals: [],
          total: 0,
          currentChemId: null,
          detailStatus: "empty",
          detail: null,
          detailError: null,
          query,
          listError: null,
        });
        return;
      }
      store.setState((prev) => {
        const currentStillVisible = d.results.some((item) => item.chem_id === prev.currentChemId);
        return {
          query,
          listStatus: "ready",
          listError: null,
          chemicals: d.results,
          total: d.total,
          currentChemId: currentStillVisible ? prev.currentChemId : null,
          detailStatus: currentStillVisible ? prev.detailStatus : "empty",
          detail: currentStillVisible ? prev.detail : null,
          detailError: currentStillVisible ? prev.detailError : null,
        };
      });
    } catch (e) {
      if (e.name === "AbortError") return;
      store.setState({
        listStatus: "error",
        listError: "서버 연결을 확인한 뒤 다시 시도하세요.",
      });
    }
  }

  async function loadDetail(chemId) {
    if (inflightDetail) inflightDetail.abort();
    inflightDetail = new AbortController();
    const { signal } = inflightDetail;
    store.setState({
      currentChemId: chemId,
      detailStatus: "loading",
      detailError: null,
      detail: null,
    });

    try {
      const d = await apiGet(`/chemicals/${encodeURIComponent(chemId)}/braille`, { signal });
      store.setState({
        currentChemId: chemId,
        detailStatus: "ready",
        detailError: null,
        detail: d,
      });
    } catch (e) {
      if (e.name === "AbortError") return;
      store.setState({
        currentChemId: chemId,
        detailStatus: "error",
        detailError: "서버 연결을 확인한 뒤 다시 시도하세요.",
        detail: null,
      });
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
    loadList(store.getState().query);
  });

  detailEl.addEventListener("click", (e) => {
    const retry = e.target.closest("[data-action='retry']");
    if (retry) {
      const { currentChemId } = store.getState();
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

  store.subscribe((nextState) => {
    renderList(nextState);
    renderDetail(nextState);
  });

  // Init
  renderList(store.getState());
  renderDetail(store.getState());
  loadList("");

  return {
    store,
    focusSearch,
    loadRandomFromList,
    loadList,
    loadDetail,
  };
}
