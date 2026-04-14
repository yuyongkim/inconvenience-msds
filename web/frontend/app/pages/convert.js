import { apiPostJson } from "../lib/api.js";
import { copyText } from "../lib/clipboard.js";
import { clear, el, qs } from "../lib/dom.js";

export function initConvert({ root, toast }) {
  const runBtn = qs(root, "#convert-run");
  const copyBtn = qs(root, "#convert-copy");
  const clearBtn = qs(root, "#convert-clear");
  const inputEl = qs(root, "#convert-input");
  const outputEl = qs(root, "#convert-output");
  const statsEl = qs(root, "#convert-stats");

  async function convertText() {
    const input = inputEl.value.trim();
    if (!input) return;
    outputEl.textContent = "변환 중...";
    statsEl.textContent = "";

    try {
      const d = await apiPostJson("/convert", { text: input });
      outputEl.textContent = d.braille;
      clear(statsEl);
      statsEl.appendChild(el("span", { text: `입력 ${d.text_chars.toLocaleString()}자` }));
      statsEl.appendChild(el("span", { text: `점자 ${d.braille_cells.toLocaleString()}셀` }));
      statsEl.appendChild(el("span", { text: `비율 ${(d.braille_cells / d.text_chars).toFixed(2)}x` }));
    } catch {
      outputEl.textContent = "변환에 실패했습니다. 서버 연결을 확인하세요.";
    }
  }

  async function copyBraille() {
    const text = outputEl.textContent;
    if (!text || text === "변환 중..." || text.startsWith("변환에 실패")) return;
    const r = await copyText(text);
    toast.show(r.ok ? "클립보드에 복사됨" : "복사에 실패했습니다");
  }

  function clearConvert() {
    inputEl.value = "";
    outputEl.textContent = "";
    statsEl.textContent = "";
  }

  runBtn.addEventListener("click", convertText);
  copyBtn.addEventListener("click", copyBraille);
  clearBtn.addEventListener("click", clearConvert);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.ctrlKey) convertText();
  });

  return { convertText, copyBraille, clearConvert };
}
