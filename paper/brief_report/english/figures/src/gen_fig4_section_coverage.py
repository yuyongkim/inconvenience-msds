"""Fig. 4 - Per-section coverage of the released dataset, recomputed from the JSONL."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figstyle import W_XBOLD, DPI_COMBO, PAGE_W, save

BLUE = "#2563EB"
BLUE_PALE = "#CFE0FF"
GREEN_FILL = "#C9F0D8"
GREEN_EDGE = "#49B677"
RED = "#E4464B"

SECTION_KO = ["1. 화학제품/회사", "2. 유해위험성", "3. 구성성분", "4. 응급조치",
              "5. 폭발화재", "6. 누출사고", "7. 취급저장", "8. 노출방지",
              "9. 물리화학", "10. 안정성", "11. 독성", "12. 환경",
              "13. 폐기", "14. 운송", "15. 법적규제", "16. 기타"]

S = json.loads((Path(__file__).with_name("fig_stats.json")).read_text(encoding="utf-8"))
TOTAL = S["n_chemicals"]
counts = [S["section_n"][str(i)] for i in range(1, 17)]
means = [S["section_mean_len"][str(i)] for i in range(1, 17)]

# "essentially every chemical" = within 0.5% of the full corpus
FULL = [c >= TOTAL * 0.995 for c in counts]

fig = plt.figure(figsize=(PAGE_W, 3.20), facecolor="white")
y = np.arange(16)[::-1]


def style(ax, labels):
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=5.7)
    ax.tick_params(axis="both", labelsize=5.7, length=2.0, width=0.5, colors="#3C4043")
    ax.set_ylim(-0.8, 15.8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#DADCE0")
    ax.spines["bottom"].set_linewidth(0.6)
    ax.set_axisbelow(True)


axa = fig.add_axes([0.135, 0.135, 0.335, 0.775])
axa.barh(y, counts, height=0.62,
         color=[BLUE if f else BLUE_PALE for f in FULL],
         edgecolor=[BLUE if f else BLUE for f in FULL], linewidth=0.35)
axa.axvline(TOTAL, color=RED, linestyle="--", linewidth=0.8)
axa.text(TOTAL * 1.02, -0.62, f"max = {TOTAL:,}", fontsize=5.2, color=RED,
         ha="left", va="center")
for yi, c in zip(y, counts):
    axa.text(c + TOTAL * 0.015, yi, f"{c:,}", va="center", ha="left", fontsize=5.3,
             color="#3C4043")
axa.set_xlim(0, TOTAL * 1.34)
axa.set_xticks([0, 10000, 20000, 30000, 40000, 50000])
axa.set_xticklabels(["0", "10K", "20K", "30K", "40K", "50K"])
axa.set_xlabel("Chemicals with non-empty section (n)", fontsize=5.8)
axa.set_title("(a) Section coverage", fontsize=6.4, weight=W_XBOLD, pad=6)
style(axa, SECTION_KO)

axb = fig.add_axes([0.605, 0.135, 0.335, 0.775])
axb.barh(y, means, height=0.62, color=GREEN_FILL, edgecolor=GREEN_EDGE,
         linewidth=0.45)
for yi, m in zip(y, means):
    axb.text(m + 12, yi, f"{m:,.0f}", va="center", ha="left", fontsize=5.3,
             color="#3C4043")
axb.set_xlim(0, max(means) * 1.20)
axb.set_xlabel("Mean Korean text length when present (chars)", fontsize=5.8)
axb.set_title("(b) Average text length per section", fontsize=6.4, weight=W_XBOLD,
              pad=6)
style(axb, SECTION_KO)

save(fig, "Fig4", DPI_COMBO)
