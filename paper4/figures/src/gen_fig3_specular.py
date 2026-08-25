"""Paper 4, Fig. 3 — how much glare a marker survives on a glossy container.

The cylinder figure answered curvature and left gloss open. This is the
synthetic bound on gloss: detection against the peak brightness of a specular
highlight, for lobes of four different widths on two container curvatures.

The vertical band is the point. Every condition holds to at least 130 out of
255 and every condition has failed by 210, so the answer is a range rather
than a line, and the lobe's width moves the boundary less than the sweep can
resolve. Drawing it as a band rather than a single threshold keeps the figure
from claiming more than the measurement supports.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "paper3" / "figures" / "src"))

from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "track-b-specular-measurements.json"

raw = json.loads(DATA.read_text(encoding="utf-8"))
grid = raw["grid"]
trials = raw["trials_per_condition"]

wraps = sorted({r["wrap"] for r in grid})
strengths = sorted({r["strength"] for r in grid})
shins = sorted({r["shininess"] for r in grid})

MARKS = ["o", "s", "^", "D"]
SHADES = ["#1A3D8F", "#3C6FD1", "#7FA3E3", "#B9CCF2"]

fig, axes = plt.subplots(1, len(wraps), figsize=(PAGE_W, 2.7), sharey=True)
fig.subplots_adjust(left=0.095, right=0.985, top=0.76, bottom=0.22, wspace=0.12)

# Shade from the last strength every condition survives to the first at which
# none does. Marking a single threshold would hide that the conditions part
# company across this span rather than falling together.
lo = min(r["highest_strength_fully_detected"] for r in grid)
hi = min(s for s in strengths
         if all(r["detected"] == 0 for r in grid if r["strength"] == s))

for ax, wrap in zip(np.atleast_1d(axes), wraps):
    ax.axvspan(lo, hi, color="#F2C9C9", alpha=0.45, zorder=0, lw=0)
    for sh, mk, col in zip(shins, MARKS, SHADES):
        pts = sorted((r for r in grid if r["wrap"] == wrap and r["shininess"] == sh),
                     key=lambda r: r["strength"])
        core = pts[0]["core_width_cells"]
        ax.plot([p["strength"] for p in pts],
                [p["detected"] / trials * 100 for p in pts],
                marker=mk, markersize=3.2, linewidth=1.1, color=col,
                label=f"n={sh} (핵 {core:.1f}칸)", zorder=3)
    ax.set_title(f"마커 폭 / 둘레 = {wrap:.2f}", fontsize=8.2, weight=W_BOLD,
                 color=INK, loc="left", pad=6)
    ax.set_xlabel("정반사 정점 밝기 (0–255)", fontsize=7.4, color=INK)
    ax.set_xticks([0, 60, 130, 190, 255])
    ax.tick_params(labelsize=7, length=0, colors=INK)
    ax.grid(color=BORDER, linewidth=0.5, alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BORDER)

first = np.atleast_1d(axes)[0]
first.set_ylabel("검출률 (%)", fontsize=7.4, color=INK)
first.set_ylim(-6, 106)
for ax in np.atleast_1d(axes):
    ax.legend(fontsize=5.9, frameon=False, loc="lower left", handlelength=1.6)

np.atleast_1d(axes)[-1].text(
    (lo + hi) / 2, 24, "조건에 따라\n갈리는 구간", ha="center", va="center",
    fontsize=6.4, color="#B02020", weight=W_BOLD, zorder=4,
)

fig.text(0.985, 0.955,
         f"합성 Blinn-Phong 하이라이트 · 정면 · 조건당 {trials}회 · 사진 아님",
         fontsize=6.2, color=GREY_TEXT, ha="right", va="top")

save_to(fig, OUT, "Fig3", DPI_LINE)
