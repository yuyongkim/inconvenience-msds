import { el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

export function renderEmptyDetail() {
  return el("div", { class: "placeholder" }, [
    el("div", { class: "empty-state" }, [
      el("div", { class: "empty-copy" }, [
        el("h3", { text: t("detail.emptyTitle") }),
        el("p", {
          text:
            t("detail.emptyDesc"),
        }),
        el("div", { class: "empty-actions" }, [
          el("button", { class: "btn btn-secondary", type: "button", "data-action": "focus-search" }, [
            t("detail.gotoSearch"),
          ]),
          el("button", { class: "btn btn-secondary", type: "button", "data-action": "random-pick" }, [
            t("detail.pickRandom"),
          ]),
        ]),
      ]),
      el("div", { class: "empty-preview" }, [
        el("div", { class: "braille-hero", html: "&#x2803;&#x2817;&#x2807;" }),
        el("div", { class: "sub", text: t("detail.emptySub") }),
      ]),
    ]),
  ]);
}

