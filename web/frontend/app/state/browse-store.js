import { createStore } from "./store.js";

const initialBrowseState = {
  query: "",
  listStatus: "idle",
  listError: null,
  chemicals: [],
  total: 0,
  selectedChemIds: [],
  bulkFormats: ["txt", "brf"],
  bulkJob: null,
  currentChemId: null,
  detailStatus: "empty",
  detailError: null,
  detail: null,
};

export function createBrowseStore() {
  return createStore(initialBrowseState);
}
