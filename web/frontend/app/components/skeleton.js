import { el } from "../lib/dom.js";

export function renderListSkeleton() {
  return el("div", {}, [
    el("div", { class: "list-header", text: "불러오는 중" }),
    el("div", { class: "skeleton" }, [
      el("div", { class: "skeleton-row" }),
      el("div", { class: "skeleton-row" }),
      el("div", { class: "skeleton-row" }),
    ]),
  ]);
}

export function renderDetailSkeleton() {
  return el("div", { class: "skeleton" }, [
    el("div", { class: "skeleton-row", style: "width: 48%" }),
    el("div", { class: "skeleton-row", style: "width: 86%" }),
    el("div", { class: "skeleton-row", style: "width: 72%" }),
  ]);
}

