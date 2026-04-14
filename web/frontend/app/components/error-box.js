import { el } from "../lib/dom.js";

export function renderErrorBox({ title, message, actionLabel } = {}) {
  const box = el("div", { class: "error-box", role: "alert" }, [
    el("strong", { text: title || "오류" }),
    el("div", { text: message || "요청을 처리할 수 없습니다." }),
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

