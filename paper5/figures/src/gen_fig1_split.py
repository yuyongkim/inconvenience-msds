"""Paper 5, Fig. 1 — what the split does to the same data.

Two bars, identical data underneath. The gap is the paper's argument, so the
figure exists to make it a single glance rather than a sentence.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "paper3" / "figures" / "src"))
from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parents[3] / "docs" / "track-c-eval-results.json"

raw = json.loads(DATA.read_text(encoding="utf-8"))
pi, rs = raw["person_independent"], raw["random_split"]

METRICS = [
    ("정확도", pi["accuracy"], rs["accuracy"]),
    ("macro 정밀도", pi["macro_precision"], rs["macro_precision"]),
    ("macro 재현율", pi["macro_recall"], rs["macro_recall"]),
]

fig, ax = plt.subplots(figsize=(PAGE_W, 2.5))
fig.subplots_adjust(left=0.13, right=0.98, top=0.80, bottom=0.26)

width = 0.34
xs = range(len(METRICS))
for i, (label, honest, inflated) in enumerate(METRICS):
    ax.bar(i - width / 2, honest, width, color=BLUE, edgecolor=NAVY,
           linewidth=0.6, zorder=3, label="signer 분리" if i == 0 else None)
    ax.bar(i + width / 2, inflated, width, color="#C9D6F0", edgecolor=NAVY,
           linewidth=0.6, zorder=3, label="무작위 분할" if i == 0 else None)
    ax.text(i - width / 2, honest + 0.003, f"{honest:.3f}", ha="center",
            va="bottom", fontsize=7.2, weight=W_BOLD, color=INK)
    ax.text(i + width / 2, inflated + 0.003, f"{inflated:.3f}", ha="center",
            va="bottom", fontsize=7.2, color=GREY_TEXT)
    ax.text(i, 0.862, f"+{(inflated - honest)*100:.1f}%p", ha="center",
            fontsize=7, color="#B02020", weight=W_BOLD, zorder=4)

ax.set_xticks(list(xs))
ax.set_xticklabels([m[0] for m in METRICS], fontsize=8, color=INK)
ax.set_ylim(0.85, 1.0)
ax.set_ylabel("점수 (축 절단)", fontsize=7.6, color=INK)
ax.tick_params(axis="y", labelsize=7, colors=GREY_TEXT)
ax.tick_params(axis="x", length=0)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(BORDER)
ax.grid(axis="y", color=BORDER, linewidth=0.5, zorder=0)
ax.set_axisbelow(True)
ax.legend(fontsize=7, frameon=False, loc="lower center", ncol=2,
          bbox_to_anchor=(0.5, -0.30))

ax.set_title("같은 데이터, 분할 방식만 다름", fontsize=9, weight=W_BOLD,
             color=INK, loc="left", pad=10)
ax.text(1.0, 1.02, "합성 keypoint · 인식 정확도 아님", transform=ax.transAxes,
        fontsize=6.6, color=GREY_TEXT, ha="right", va="bottom")

save_to(fig, OUT, "Fig1", DPI_LINE)
