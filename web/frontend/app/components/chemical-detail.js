import { clear, el } from "../lib/dom.js";

function formatRatio(stats) {
  if (!stats || !stats.korean_chars || stats.korean_chars <= 0) return "—";
  return (stats.braille_cells / stats.korean_chars).toFixed(2);
}

export function renderChemicalDetail({ detailEl, chem }) {
  clear(detailEl);

  const ratio = formatRatio(chem.stats);
  const header = el("div", { class: "detail-header" }, [
    el("h2", { text: chem.name }),
    el("div", { class: "detail-meta" }, [
      el("span", { class: "meta-chip", text: `ID ${chem.chem_id}` }),
      el("span", { class: "meta-chip", text: `한국어 ${Number(chem.stats?.korean_chars ?? 0).toLocaleString()}자` }),
      el("span", { class: "meta-chip", text: `점자 ${Number(chem.stats?.braille_cells ?? 0).toLocaleString()}셀` }),
      el("span", { class: "meta-chip", text: `비율 ${ratio}x` }),
    ]),
  ]);

  const download = el("div", { class: "download-row" }, [
    el(
      "a",
      {
        class: "btn btn-primary",
        href: `/api/chemicals/${encodeURIComponent(chem.chem_id)}/braille.txt`,
        download: "",
      },
      ["Unicode TXT"],
    ),
    el(
      "a",
      {
        class: "btn btn-secondary",
        href: `/api/chemicals/${encodeURIComponent(chem.chem_id)}/braille.brf`,
        download: "",
      },
      ["BRF (엠보서)"],
    ),
  ]);

  const body = el("div", { class: "detail-body" });
  for (const sec of chem.sections ?? []) {
    const title = el(
      "div",
      { class: "section-title", role: "button", tabindex: "0", "data-action": "toggle-section" },
      [el("span", { text: `${sec.section_no}. ${sec.title}` }), el("span", { class: "toggle", text: "접기/펼치기" })],
    );
    const korean = el("div", { class: "section-korean" }, [
      el("div", { class: "col-label", text: "한국어" }),
      el("div", { text: sec.korean }),
    ]);
    const braille = el("div", { class: "section-braille" }, [
      el("div", { class: "col-label", text: "점자" }),
      el("div", { text: sec.braille }),
    ]);
    const content = el("div", { class: "section-content" }, [korean, braille]);
    body.appendChild(el("div", { class: "section" }, [title, content]));
  }

  detailEl.appendChild(header);
  detailEl.appendChild(download);
  detailEl.appendChild(body);
}

