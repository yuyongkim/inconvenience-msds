"""Fig 4 — Per-section coverage. Two output sets:
  English labels  → fig_section_coverage.{pdf,png}     (main.tex)
  Korean labels   → fig_section_coverage_ko.{pdf,png}  (main_ko.tex)
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

ROOT = Path(r"C:\Users\USER\Desktop\Braille")
JSONL = ROOT / "data" / "hf_dataset" / "train.jsonl"
OUT_DIR = ROOT / "paper" / "archive" / "tex_source"

KOR_FONT = r"C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts\NanumSquareNeo-bRg.ttf"
fm.fontManager.addfont(KOR_FONT)
KOR_FAMILY = fm.FontProperties(fname=KOR_FONT).get_name()

SECTION_EN = {
    1: "1. Identification",
    2: "2. Hazards",
    3: "3. Composition",
    4: "4. First aid",
    5: "5. Fire / explosion",
    6: "6. Release / spill",
    7: "7. Handling / storage",
    8: "8. Exposure controls",
    9: "9. Phys. / chem.",
    10: "10. Stability",
    11: "11. Toxicology",
    12: "12. Ecology",
    13: "13. Disposal",
    14: "14. Transport",
    15: "15. Regulation",
    16: "16. Other",
}
SECTION_KO = {
    1: "1. 화학제품/회사",
    2: "2. 유해·위험성",
    3: "3. 구성성분",
    4: "4. 응급조치",
    5: "5. 폭발·화재",
    6: "6. 누출사고",
    7: "7. 취급·저장",
    8: "8. 노출방지",
    9: "9. 물리화학",
    10: "10. 안정성",
    11: "11. 독성",
    12: "12. 환경",
    13: "13. 폐기",
    14: "14. 운송",
    15: "15. 법적규제",
    16: "16. 기타",
}

TOTAL = 48966
section_n = Counter()
section_chars = defaultdict(list)

with open(JSONL, "r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        for s in d["sections"]:
            no = s.get("section_no")
            if no is None:
                continue
            txt = s.get("text_ko") or ""
            if txt.strip():
                section_n[no] += 1
                section_chars[no].append(len(txt))

xs = list(range(1, 17))
counts = [section_n[i] for i in xs]
avgs = [sum(section_chars[i]) / max(len(section_chars[i]), 1) for i in xs]


def render(lang: str, out_stem: str):
    is_ko = lang == "ko"
    plt.rcParams["font.family"] = KOR_FAMILY if is_ko else "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    section_map = SECTION_KO if is_ko else SECTION_EN
    labels = [section_map[i] for i in xs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

    ax1.bar(xs, counts, color="#4285F4", edgecolor="white")
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    if is_ko:
        ax1.set_ylabel("비어 있지 않은 섹션 보유 화학물질 수", fontsize=11)
        ax1.set_title(f"(a) 섹션 커버리지 ({TOTAL:,}종 화학물질 대상)",
                      fontsize=12, fontweight="bold", pad=10)
        max_lbl = f"최대 = {TOTAL:,}"
        ax2_ylabel = "비어 있지 않을 때 평균 한국어 본문 길이 (문자)"
        ax2_title = "(b) 섹션별 평균 한국어 본문 길이"
    else:
        ax1.set_ylabel("Chemicals with non-empty section (n)", fontsize=11)
        ax1.set_title(f"(a) Section coverage across {TOTAL:,} chemicals",
                      fontsize=12, fontweight="bold", pad=10)
        max_lbl = f"max = {TOTAL:,}"
        ax2_ylabel = "Mean Korean text length when present (chars)"
        ax2_title = "(b) Average Korean text length per section"

    ax1.axhline(TOTAL, color="#EA4335", linestyle="--", linewidth=1, label=max_lbl)
    ax1.legend(fontsize=9)
    for x, v in zip(xs, counts):
        ax1.text(x, v + 800, f"{v//1000}K", ha="center", fontsize=7)
    ax1.set_ylim(0, TOTAL * 1.10)

    ax2.bar(xs, avgs, color="#34A853", edgecolor="white")
    ax2.set_xticks(xs)
    ax2.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax2.set_ylabel(ax2_ylabel, fontsize=11)
    ax2.set_title(ax2_title, fontsize=12, fontweight="bold", pad=10)

    fig.tight_layout()
    pdf = OUT_DIR / f"{out_stem}.pdf"
    png = OUT_DIR / f"{out_stem}.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Wrote {pdf} and {png}")


render("en", "fig_section_coverage")
render("ko", "fig_section_coverage_ko")
print(f"Total nonempty sections: {sum(counts)}")
