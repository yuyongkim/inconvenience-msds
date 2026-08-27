"""Fig 5: per-section coverage of the released JSONL dataset.

Left:  bar chart of nonempty-section counts (out of 48,966 chemicals).
Right: average Korean text length per section (where nonempty).
"""
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

ROOT = Path(__file__).resolve().parent.parent
JSONL = ROOT / "data" / "hf_dataset" / "train.jsonl"

FONT = r"C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts\NanumSquareNeo-bRg.ttf"
fm.fontManager.addfont(FONT)
plt.rcParams["font.family"] = fm.FontProperties(fname=FONT).get_name()
plt.rcParams["axes.unicode_minus"] = False

SECTION_TITLES = {
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0))

xs = list(range(1, 17))
labels = [SECTION_TITLES[i] for i in xs]
counts = [section_n[i] for i in xs]
ax1.bar(xs, counts, color="#4285F4", edgecolor="white")
ax1.set_xticks(xs)
ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
ax1.set_ylabel("Chemicals with non-empty section (n)", fontsize=11)
ax1.set_title(f"(a) Section coverage across {TOTAL:,} chemicals",
              fontsize=12, fontweight="bold", pad=10)
ax1.axhline(TOTAL, color="#EA4335", linestyle="--", linewidth=1,
            label=f"max = {TOTAL:,}")
ax1.legend(fontsize=9)
for x, v in zip(xs, counts):
    ax1.text(x, v + 800, f"{v//1000}K", ha="center", fontsize=7)
ax1.set_ylim(0, TOTAL * 1.10)

avgs = [sum(section_chars[i]) / max(len(section_chars[i]), 1) for i in xs]
ax2.bar(xs, avgs, color="#34A853", edgecolor="white")
ax2.set_xticks(xs)
ax2.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
ax2.set_ylabel("Mean Korean text length when present (chars)", fontsize=11)
ax2.set_title("(b) Average Korean text length per section",
              fontsize=12, fontweight="bold", pad=10)

fig.tight_layout()
out_pdf = ROOT / "paper" / "fig_section_coverage.pdf"
out_png = ROOT / "paper" / "fig_section_coverage.png"
fig.savefig(out_pdf, bbox_inches="tight")
fig.savefig(out_png, bbox_inches="tight", dpi=300)
print(f"Wrote {out_pdf} and {out_png}")
print("Section nonempty counts:", dict(section_n))
print("Total nonempty sections:", sum(section_n.values()))
