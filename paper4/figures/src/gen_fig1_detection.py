"""Paper 4, Fig. 1 — ArUco detection as a heat map over marker size and angle.

The claim the figure has to carry is not "it works" but "size binds before angle
does". A grid makes that visible: the failing cells cluster at the bottom, not
at the right.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "paper3" / "figures" / "src"))
from figbase import (BORDER, DPI_LINE, GREY_TEXT, INK, NAVY,  # noqa: E402
                     PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parents[3] / "docs" / "track-b-marker-measurements.json"

raw = json.loads(DATA.read_text(encoding="utf-8"))
matrix = raw["size_angle_matrix"]
trials = raw["trials_per_condition"]
frame_w = raw["frame"]["w"]

sizes = sorted({r["marker_px"] for r in matrix}, reverse=True)
angles = sorted({r["angle_deg"] for r in matrix})
grid = np.array([[next(r["detected"] for r in matrix
                       if r["marker_px"] == s and r["angle_deg"] == a) / trials
                  for a in angles] for s in sizes])

fig, ax = plt.subplots(figsize=(PAGE_W, 2.7))
fig.subplots_adjust(left=0.19, right=0.99, top=0.83, bottom=0.19)

cmap = plt.cm.Blues
im = ax.imshow(grid, cmap=cmap, vmin=0, vmax=1, aspect="auto")

for i, s in enumerate(sizes):
    for j, a in enumerate(angles):
        v = grid[i, j]
        ax.text(j, i, f"{v*100:.0f}", ha="center", va="center", fontsize=7,
                weight=W_BOLD if v < 0.999 else 400,
                color="white" if v > 0.55 else ("#B02020" if v < 0.999 else INK))

ax.set_xticks(range(len(angles)))
ax.set_xticklabels([f"{a}°" for a in angles], fontsize=7.4, color=INK)
ax.set_yticks(range(len(sizes)))
ax.set_yticklabels([f"{s}px  ({s/frame_w*100:.1f}%)" for s in sizes],
                   fontsize=7.2, color=INK)
ax.set_xlabel("카메라 축에서 벗어난 각도", fontsize=7.6, color=INK)
ax.set_ylabel("마커 크기 (화면 폭 대비)", fontsize=7.6, color=INK)
ax.tick_params(length=0)
for side in ("top", "right", "left", "bottom"):
    ax.spines[side].set_color(BORDER)

ax.set_title(f"ArUco 검출률 (%), 조건당 {trials}회",
             fontsize=9, weight=W_BOLD, color=INK, loc="left", pad=8)
ax.text(1.0, 1.04, "합성 장면 · 상한값", transform=ax.transAxes,
        fontsize=6.6, color=GREY_TEXT, ha="right", va="bottom")

save_to(fig, OUT, "Fig1", DPI_LINE)
