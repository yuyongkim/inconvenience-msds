import { el } from "../lib/dom.js";

export function renderListEmpty() {
  return el("div", {}, [
    el("div", { class: "list-header", text: "결과 없음" }),
    el("div", { class: "loader", text: "다른 키워드로 다시 검색해 보세요" }),
  ]);
}

