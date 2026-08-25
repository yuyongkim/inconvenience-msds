"""Paper 3, Fig. 1 — root coverage across three name catalogues.

The bars carry the paper's central result, including the negative one: the
pharmaceutical bar is short because the strings measured were product names, not
ingredient names, and the annotation says so on the figure rather than leaving
it to the caption.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]

DOMAINS = [
    ("KOSHA 화학물질\n(출처 도메인)", 40.4, 9903, False),
    ("WHO INN 라디칼\n(영문)", 8.5, 690, False),
    ("MFDS 의약품\n제품명", 1.5, 4762, True),
]

fig, ax = plt.subplots(figsize=(PAGE_W, 2.5))
fig.subplots_adjust(left=0.235, right=0.97, top=0.86, bottom=0.24)

ys = range(len(DOMAINS))
for y, (label, pct, n, flagged) in zip(ys, DOMAINS):
    ax.barh(y, pct, height=0.52, color="#C9D6F0" if flagged else BLUE,
            edgecolor=NAVY, linewidth=0.6, zorder=3)
    ax.text(pct + 1.2, y, f"{pct}%", va="center", ha="left",
            fontsize=8.5, weight=W_BOLD, color=INK, zorder=4)
    ax.text(pct + 6.5, y, f"n={n:,}", va="center", ha="left",
            fontsize=7, color=GREY_TEXT, zorder=4)

ax.set_yticks(list(ys))
ax.set_yticklabels([d[0] for d in DOMAINS], fontsize=7.6, color=INK)
ax.invert_yaxis()
ax.set_xlim(0, 56)
ax.set_xlabel("어근으로 설명되는 이름 글자의 비율 (%)", fontsize=7.6, color=INK)
ax.tick_params(axis="x", labelsize=7, colors=GREY_TEXT)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(BORDER)
ax.grid(axis="x", color=BORDER, linewidth=0.5, zorder=0)
ax.set_axisbelow(True)

ax.text(
    14, 2, "제품명은 브랜드명이라 라틴 어근이 없다",
    fontsize=6.9, color=GREY_TEXT, va="center", ha="left", zorder=4,
)
ax.set_title("어근 사전 125개의 도메인별 도달 범위", fontsize=9,
             weight=W_BOLD, color=INK, loc="left", pad=8)

save_to(fig, OUT, "Fig1", DPI_LINE)
