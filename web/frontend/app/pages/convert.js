import { apiPostJson } from "../lib/api.js";
import { copyText } from "../lib/clipboard.js";
import { clear, el, qs } from "../lib/dom.js";
import { t } from "../lib/i18n.js";

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
    outputEl.textContent = t("convert.running");
    statsEl.textContent = "";

    try {
      const d = await apiPostJson("/convert", { text: input });
      outputEl.textContent = d.braille;
      clear(statsEl);
      statsEl.appendChild(el("span", { text: t("convert.inputChars", { n: d.text_chars.toLocaleString() }) }));
      statsEl.appendChild(el("span", { text: t("detail.brailleCells", { n: d.braille_cells.toLocaleString() }) }));
      statsEl.appendChild(
        el("span", { text: t("detail.ratio", { n: (d.braille_cells / d.text_chars).toFixed(2) }) })
      );
    } catch {
      outputEl.textContent = t("convert.failed");
    }
  }

  async function copyBraille() {
    const text = outputEl.textContent;
    if (!text || text === t("convert.running") || text === t("convert.failed")) return;
    const r = await copyText(text);
    toast.show(r.ok ? t("convert.copied") : t("convert.copyFailed"));
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
