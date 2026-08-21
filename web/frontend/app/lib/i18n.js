/**
 * UI strings in Korean and English.
 *
 * The corpus and the MSDS text itself stay Korean — this covers the interface
 * only, so that a reader who cannot read Korean can still reach the data and
 * the download formats.
 *
 * `document.documentElement.lang` follows the choice. Screen readers pick their
 * voice from that attribute, so leaving it on "ko" while showing English would
 * have the page read aloud in a Korean voice.
 */

const STORAGE_KEY = "kosha-braille-lang";

const STRINGS = {
  ko: {
    "meta.title": "KOSHA-Braille — 화학물질 안전보건자료 점자 변환",
    "meta.description": "한국 등록 48,966종 화학물질 MSDS를 점자로 변환하는 웹 서비스",
    "header.sub": "화학물질 안전보건자료 점자 변환",
    "lang.toggle": "English",
    "lang.toggleLabel": "Switch to English",

    "tab.browse": "화학물질 검색",
    "tab.convert": "실시간 변환",

    "hero.label": "서비스 소개",
    "hero.titleBefore": "MSDS를 ",
    "hero.titleStrong": "점자",
    "hero.titleAfter": "로 변환하고 바로 내려받습니다",
    "hero.desc": "화학물질 안전보건자료의 본문을 한국 점자 규정(2017) 기준으로 변환합니다. Unicode 점자와 엠보서용 BRF를 지원합니다.",

    "search.placeholder": "화학물질명 또는 CAS 번호 검색",
    "search.submit": "검색",
    "search.clear": "초기화",
    "search.reset": "검색 조건이 초기화되었습니다",

    "bulk.label": "벌크 다운로드",
    "bulk.idle": "선택한 항목을 ZIP으로 묶어 다운로드할 수 있습니다.",
    "bulk.queued": "ZIP 작업 대기 중 · {done}/{total}",
    "bulk.running": "ZIP 생성 중 · {done}/{total}",
    "bulk.done": "ZIP 준비 완료 · 성공 {done}, 실패 {failed}",
    "bulk.failed": "ZIP 생성에 실패했습니다.",
    "bulk.count": "선택 {n}개",
    "bulk.format": "포맷",
    "bulk.selectVisible": "현재 목록 선택",
    "bulk.clearSelected": "선택 해제",
    "bulk.create": "ZIP 생성",
    "bulk.download": "ZIP 다운로드",
    "bulk.added": "현재 목록을 선택 항목에 추가했습니다",
    "bulk.cleared": "선택 항목을 비웠습니다",
    "bulk.needFormat": "최소 한 가지 포맷은 선택해야 합니다",
    "bulk.needSelection": "먼저 항목을 선택하세요",
    "bulk.started": "ZIP 작업을 시작했습니다",
    "bulk.startFailed": "ZIP 작업을 시작하지 못했습니다.",
    "bulk.statusFailed": "ZIP 작업 상태를 불러오지 못했습니다.",

    "list.loading": "목록 불러오는 중",
    "list.shown": "{total}개 중 {shown}개 표시",
    "list.empty": "결과 없음",
    "list.emptyHint": "다른 키워드로 다시 검색해 보세요",
    "list.error": "목록을 불러오지 못했습니다",

    "detail.error": "상세 정보를 불러오지 못했습니다",
    "detail.emptyTitle": "왼쪽 목록에서 화학물질을 선택하세요",
    "detail.emptyDesc": "검색하거나 목록을 클릭하면 MSDS 전문이 점자로 변환됩니다. 변환 결과는 섹션별로 한국어/점자를 나란히 확인할 수 있습니다.",
    "detail.gotoSearch": "검색창으로 이동",
    "detail.pickRandom": "목록에서 임의 선택",
    "detail.emptySub": "선택 후 다운로드 버튼에서 Unicode TXT / BRF를 내려받을 수 있습니다.",
    "detail.koreanChars": "한국어 {n}자",
    "detail.brailleCells": "점자 {n}셀",
    "detail.ratio": "비율 {n}x",
    "detail.brf": "BRF (엠보서)",
    "detail.toggle": "접기/펼치기",
    "detail.korean": "한국어",
    "detail.braille": "점자",

    "convert.run": "점자로 변환",
    "convert.copy": "복사",
    "convert.clear": "초기화",
    "convert.hint": "Ctrl+Enter로 변환",
    "convert.inputLabel": "한국어 텍스트",
    "convert.outputLabel": "점자 출력",
    "convert.placeholder": "여기에 한국어 텍스트를 입력하세요.\n\n예: 벤젠은 방향족 탄화수소로, 무색의 휘발성 액체입니다.",
    "convert.running": "변환 중...",
    "convert.failed": "변환에 실패했습니다. 서버 연결을 확인하세요.",
    "convert.inputChars": "입력 {n}자",
    "convert.copied": "클립보드에 복사됨",
    "convert.copyFailed": "복사에 실패했습니다",

    "stats.chemicals": " 화학물질",
    "stats.sections": " MSDS 섹션",
    "stats.complete": " 완전(15+)",

    "error.title": "오류",
    "error.generic": "요청을 처리할 수 없습니다.",
    "error.connection": "서버 연결을 확인한 뒤 다시 시도하세요.",
    "error.retry": "다시 시도",
    "common.loading": "불러오는 중",

    "footer": "KOSHA-Braille · 한국 점자 규정 (2017) 기반 · 48,966종 화학물질",
  },

  en: {
    "meta.title": "KOSHA-Braille — Korean chemical safety data sheets in braille",
    "meta.description":
      "Web service converting the MSDS records of 48,966 chemicals registered in Korea into Korean braille",
    "header.sub": "Korean chemical safety data sheets in braille",
    "lang.toggle": "한국어",
    "lang.toggleLabel": "한국어로 전환",

    "tab.browse": "Browse chemicals",
    "tab.convert": "Live conversion",

    "hero.label": "About this service",
    "hero.titleBefore": "Turn an MSDS into ",
    "hero.titleStrong": "braille",
    "hero.titleAfter": " and download it right away",
    "hero.desc": "Converts the body text of Korean chemical safety data sheets under the 2017 Korean Braille Standards. Unicode braille and embosser-ready BRF are both supported.",

    "search.placeholder": "Search by chemical name or CAS number",
    "search.submit": "Search",
    "search.clear": "Reset",
    "search.reset": "Search filters cleared",

    "bulk.label": "Bulk download",
    "bulk.idle": "Selected chemicals can be downloaded together as a ZIP archive.",
    "bulk.queued": "ZIP job queued · {done}/{total}",
    "bulk.running": "Building ZIP · {done}/{total}",
    "bulk.done": "ZIP ready · {done} succeeded, {failed} failed",
    "bulk.failed": "Could not build the ZIP archive.",
    "bulk.count": "{n} selected",
    "bulk.format": "Formats",
    "bulk.selectVisible": "Select current page",
    "bulk.clearSelected": "Clear selection",
    "bulk.create": "Build ZIP",
    "bulk.download": "Download ZIP",
    "bulk.added": "Current page added to the selection",
    "bulk.cleared": "Selection cleared",
    "bulk.needFormat": "Choose at least one format",
    "bulk.needSelection": "Select some chemicals first",
    "bulk.started": "ZIP job started",
    "bulk.startFailed": "Could not start the ZIP job.",
    "bulk.statusFailed": "Could not read the ZIP job status.",

    "list.loading": "Loading chemicals",
    "list.shown": "Showing {shown} of {total}",
    "list.empty": "No results",
    "list.emptyHint": "Try a different search term",
    "list.error": "Could not load the chemical list",

    "detail.error": "Could not load this chemical",
    "detail.emptyTitle": "Pick a chemical from the list",
    "detail.emptyDesc": "Search or click an entry and its full MSDS is converted to braille. Each section shows the Korean text and the braille side by side.",
    "detail.gotoSearch": "Go to search",
    "detail.pickRandom": "Pick one at random",
    "detail.emptySub": "Once selected, the download buttons give you Unicode TXT and BRF.",
    "detail.koreanChars": "{n} Korean characters",
    "detail.brailleCells": "{n} braille cells",
    "detail.ratio": "ratio {n}x",
    "detail.brf": "BRF (embosser)",
    "detail.toggle": "Expand / collapse",
    "detail.korean": "Korean",
    "detail.braille": "Braille",

    "convert.run": "Convert to braille",
    "convert.copy": "Copy",
    "convert.clear": "Clear",
    "convert.hint": "Ctrl+Enter to convert",
    "convert.inputLabel": "Korean text",
    "convert.outputLabel": "Braille output",
    "convert.placeholder": "Type Korean text here.\n\nExample: 벤젠은 방향족 탄화수소로, 무색의 휘발성 액체입니다.",
    "convert.running": "Converting…",
    "convert.failed": "Conversion failed. Check the server connection.",
    "convert.inputChars": "{n} characters in",
    "convert.copied": "Copied to clipboard",
    "convert.copyFailed": "Could not copy",

    "stats.chemicals": " chemicals",
    "stats.sections": " MSDS sections",
    "stats.complete": " complete (15+)",

    "error.title": "Error",
    "error.generic": "The request could not be completed.",
    "error.connection": "Check the server connection and try again.",
    "error.retry": "Try again",
    "common.loading": "Loading",

    "footer": "KOSHA-Braille · Built on the 2017 Korean Braille Standards · 48,966 chemicals",
  },
};

function detectLang() {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved && STRINGS[saved]) return saved;
  } catch {
    // localStorage can be blocked; fall through to the browser preference.
  }
  const preferred = navigator.languages?.[0] || navigator.language || "ko";
  return preferred.toLowerCase().startsWith("ko") ? "ko" : "en";
}

let current = detectLang();
const listeners = new Set();

export function getLang() {
  return current;
}

export function t(key, params) {
  const table = STRINGS[current] || STRINGS.ko;
  let out = table[key];
  if (out === undefined) return key;
  if (params) {
    for (const [name, value] of Object.entries(params)) {
      out = out.split("{" + name + "}").join(String(value));
    }
  }
  return out;
}

export function setLang(lang) {
  if (!STRINGS[lang] || lang === current) return;
  current = lang;
  try {
    window.localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // Not being able to remember the choice is not worth failing over.
  }
  applyStaticText();
  for (const fn of listeners) fn(lang);
}

export function onLangChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Fill every element carrying a data-i18n* attribute, and the document itself. */
export function applyStaticText(root = document) {
  document.documentElement.lang = current;
  document.title = t("meta.title");

  const desc = document.querySelector('meta[name="description"]');
  if (desc) desc.setAttribute("content", t("meta.description"));

  for (const node of root.querySelectorAll("[data-i18n]")) {
    node.textContent = t(node.dataset.i18n);
  }
  for (const node of root.querySelectorAll("[data-i18n-placeholder]")) {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  }
  for (const node of root.querySelectorAll("[data-i18n-label]")) {
    node.setAttribute("aria-label", t(node.dataset.i18nLabel));
  }
}

/** Wire the toggle button. */
export function initLangToggle(button) {
  if (!button) return;
  const paint = () => {
    button.textContent = t("lang.toggle");
    button.setAttribute("aria-label", t("lang.toggleLabel"));
    // The label is written in the language it switches *to*.
    button.lang = current === "ko" ? "en" : "ko";
  };
  button.addEventListener("click", () => setLang(current === "ko" ? "en" : "ko"));
  onLangChange(paint);
  paint();
}
