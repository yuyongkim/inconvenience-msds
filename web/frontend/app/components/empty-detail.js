import { el } from "../lib/dom.js";

export function renderEmptyDetail() {
  return el("div", { class: "placeholder" }, [
    el("div", { class: "empty-state" }, [
      el("div", { class: "empty-copy" }, [
        el("h3", { text: "왼쪽 목록에서 화학물질을 선택하세요" }),
        el("p", {
          text:
            "검색하거나 목록을 클릭하면 MSDS 전문이 점자로 변환됩니다. 변환 결과는 섹션별로 한국어/점자를 나란히 확인할 수 있습니다.",
        }),
        el("div", { class: "empty-actions" }, [
          el("button", { class: "btn btn-secondary", type: "button", "data-action": "focus-search" }, [
            "검색창으로 이동",
          ]),
          el("button", { class: "btn btn-secondary", type: "button", "data-action": "random-pick" }, [
            "목록에서 임의 선택",
          ]),
        ]),
      ]),
      el("div", { class: "empty-preview" }, [
        el("div", { class: "braille-hero", html: "&#x2803;&#x2817;&#x2807;" }),
        el("div", { class: "sub", text: "선택 후 다운로드 버튼에서 Unicode TXT / BRF를 내려받을 수 있습니다." }),
      ]),
    ]),
  ]);
}

