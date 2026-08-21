import { el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

export function renderListEmpty() {
  return el("div", {}, [
    el("div", { class: "list-header", text: t("list.empty") }),
    el("div", { class: "loader", text: t("list.emptyHint") }),
  ]);
}

