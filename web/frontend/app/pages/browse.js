import { apiGet, apiPostJson } from "../lib/api.js";
import { clear, qs } from "../lib/dom.js";
import { renderListSkeleton, renderDetailSkeleton } from "../components/skeleton.js";
import { renderErrorBox } from "../components/error-box.js";
import { renderEmptyDetail } from "../components/empty-detail.js";
import { renderListEmpty } from "../components/list-empty.js";
import { renderBulkToolbar } from "../components/bulk-toolbar.js";
import { renderChemicalList, setListSelection } from "../components/chemical-list.js";
import { renderChemicalDetail } from "../components/chemical-detail.js";
import { createBrowseStore } from "../state/browse-store.js";
import { t } from "../lib/i18n.js";

export function initBrowse({ root, toast }) {
  const listEl = qs(root, "#list");
  const detailEl = qs(root, "#detail");
  const bulkToolbarEl = qs(root, "#bulk-toolbar");
  const searchForm = qs(root, "#search-form");
  const searchInput = qs(root, "#search-input");
  const clearBtn = qs(root, "#search-clear");
  const store = createBrowseStore();

  let inflightList = null;
  let inflightDetail = null;
  let bulkPollTimer = null;

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

  function stopBulkPolling() {
    if (bulkPollTimer) {
      window.clearTimeout(bulkPollTimer);
      bulkPollTimer = null;
    }
  }

  function scheduleBulkPoll(jobId) {
    stopBulkPolling();
    bulkPollTimer = window.setTimeout(async () => {
      try {
        const job = await apiGet(`/bulk-jobs/${encodeURIComponent(jobId)}`);
        store.setState({ bulkJob: job });
        if (job.status === "queued" || job.status === "running") {
          scheduleBulkPoll(jobId);
        }
      } catch {
        store.setState({
          bulkJob: {
            ...(store.getState().bulkJob || {}),
            status: "failed",
            error: t("bulk.statusFailed"),
          },
        });
      }
    }, 1000);
  }

  function setSelectedChemIds(nextIds) {
    store.setState({
      selectedChemIds: Array.from(new Set(nextIds)),
    });
  }

  function toggleSelection(chemId, checked) {
    const prev = store.getState().selectedChemIds;
    if (checked) {
      setSelectedChemIds([...prev, chemId]);
      return;
    }
    setSelectedChemIds(prev.filter((id) => id !== chemId));
  }

  function selectVisible() {
    const ids = store.getState().chemicals.map((item) => item.chem_id);
    setSelectedChemIds([...store.getState().selectedChemIds, ...ids]);
    toast.show(t("bulk.added"));
  }

  function clearSelected() {
    store.setState({ selectedChemIds: [] });
    toast.show(t("bulk.cleared"));
  }

  function toggleBulkFormat(format, checked) {
    const prev = store.getState().bulkFormats;
    if (!checked && prev.length === 1 && prev.includes(format)) {
      renderBulkToolbar({ mountEl: bulkToolbarEl, state: store.getState() });
      toast.show(t("bulk.needFormat"));
      return;
    }
    if (checked) {
      store.setState({ bulkFormats: Array.from(new Set([...prev, format])) });
      return;
    }
    store.setState({ bulkFormats: prev.filter((value) => value !== format) });
  }

  async function createBulkJob() {
    const state = store.getState();
    if (state.selectedChemIds.length === 0) {
      toast.show(t("bulk.needSelection"));
      return;
    }

    try {
      const job = await apiPostJson("/bulk-jobs", {
        chem_ids: state.selectedChemIds,
        formats: state.bulkFormats,
      });
      store.setState({ bulkJob: job });
      scheduleBulkPoll(job.job_id);
      toast.show(t("bulk.started"));
    } catch {
      store.setState({
        bulkJob: {
          job_id: "",
          status: "failed",
          error: t("bulk.startFailed"),
          created_at: "",
          completed_at: null,
          formats: state.bulkFormats,
          total_items: state.selectedChemIds.length,
          completed_items: 0,
          failed_items: 0,
          download_url: null,
        },
      });
    }
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
          title: t("list.error"),
          message: state.listError || t("error.connection"),
          actionLabel: t("error.retry"),
        }),
      );
      return;
    }
    if (state.listStatus === "empty") {
      listEl.appendChild(renderListEmpty());
      return;
    }

    renderChemicalList({
      listEl,
      chemicals: state.chemicals,
      total: state.total,
      selectedChemIds: state.selectedChemIds,
    });
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
          title: t("detail.error"),
          message: state.detailError || t("error.connection"),
          actionLabel: t("error.retry"),
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
        listError: t("error.connection"),
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
        detailError: t("error.connection"),
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
    toast.show(t("search.reset"));
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

  listEl.addEventListener("change", (e) => {
    const input = e.target.closest("input[data-select-chem-id]");
    if (!input) return;
    toggleSelection(input.dataset.selectChemId, input.checked);
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

  bulkToolbarEl.addEventListener("click", (e) => {
    const action = e.target.closest("[data-action]");
    if (!action) return;
    const actionName = action.dataset.action;
    if (actionName === "select-visible") {
      selectVisible();
      return;
    }
    if (actionName === "clear-selected") {
      clearSelected();
      return;
    }
    if (actionName === "create-bulk-job") {
      createBulkJob();
    }
  });

  bulkToolbarEl.addEventListener("change", (e) => {
    const input = e.target.closest("input[data-format]");
    if (!input) return;
    toggleBulkFormat(input.dataset.format, input.checked);
  });

  store.subscribe((nextState) => {
    renderList(nextState);
    renderDetail(nextState);
    renderBulkToolbar({ mountEl: bulkToolbarEl, state: nextState });
  });

  // Init
  renderList(store.getState());
  renderDetail(store.getState());
  renderBulkToolbar({ mountEl: bulkToolbarEl, state: store.getState() });
  loadList("");

  return {
    store,
    focusSearch,
    loadRandomFromList,
    loadList,
    loadDetail,
  };
}
