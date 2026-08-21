import { el } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

export function renderErrorBox({ title, message, actionLabel } = {}) {
  const box = el("div", { class: "error-box", role: "alert" }, [
    el("strong", { text: title || t("error.title") }),
    el("div", { text: message || t("error.generic") }),
  ]);

  if (actionLabel) {
    box.appendChild(
      el("div", { class: "empty-actions", style: "margin-top: 12px" }, [
        el(
          "button",
          { class: "btn btn-secondary", type: "button", "data-action": "retry" },
          [actionLabel],
        ),
      ]),
    );
  }

  return box;
}

