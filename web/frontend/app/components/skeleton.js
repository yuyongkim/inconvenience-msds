import { el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

export function renderListSkeleton() {
  return el("div", {}, [
    el("div", { class: "list-header", text: t("common.loading") }),
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

