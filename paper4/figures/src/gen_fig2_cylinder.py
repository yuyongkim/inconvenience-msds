"""Paper 4, Fig. 2 — angle tolerance collapses on a curved container.

The planar figure says 70°. This one says what happens when the same marker is
wrapped around a bottle, which is what cosmetics packaging is. Placing the two
side by side is the point: the flat row is the top line, and every row below it
is a real container.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "paper3" / "figures" / "src"))
from figbase import (BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parents[3] / "docs" / "track-b-cylinder-measurements.json"

raw = json.loads(DATA.read_text(encoding="utf-8"))
grid = raw["grid"]
trials = raw["trials_per_condition"]

wraps = sorted({r["wrap"] for r in grid})
angles = sorted({r["angle_deg"] for r in grid})
mat = np.array([[next(r["detected"] for r in grid
                      if r["wrap"] == w and r["angle_deg"] == a) / trials
                 for a in angles] for w in wraps])

LABELS = {
    0.0: "평면 (라벨 카드)",
    0.10: "0.10 · 넓은 단지 지름 70mm",
    0.20: "0.20 · 세럼 병 지름 30mm",
    0.30: "0.30",
    0.40: "0.40 · 립밤 지름 16mm",
    0.50: "0.50",
}

fig, ax = plt.subplots(figsize=(PAGE_W, 2.6))
fig.subplots_adjust(left=0.30, right=0.99, top=0.82, bottom=0.20)

ax.imshow(mat, cmap=plt.cm.Blues, vmin=0, vmax=1, aspect="auto")
for i in range(len(wraps)):
    for j in range(len(angles)):
        v = mat[i, j]
        ax.text(j, i, f"{v*100:.0f}", ha="center", va="center", fontsize=7,
                weight=W_BOLD if v < 0.999 else 400,
                color="white" if v > 0.55 else "#B02020")

ax.set_xticks(range(len(angles)))
ax.set_xticklabels([f"{a}°" for a in angles], fontsize=7.4, color=INK)
ax.set_yticks(range(len(wraps)))
ax.set_yticklabels([LABELS.get(w, f"{w:.2f}") for w in wraps], fontsize=7, color=INK)
ax.set_xlabel("카메라 축에서 벗어난 각도", fontsize=7.6, color=INK)
ax.set_ylabel("마커 폭 / 용기 둘레", fontsize=7.6, color=INK)
ax.tick_params(length=0)
for side in ("top", "right", "left", "bottom"):
    ax.spines[side].set_color(BORDER)

ax.set_title("원통면에서의 ArUco 검출률 (%), 마커 120px", fontsize=9,
             weight=W_BOLD, color=INK, loc="left", pad=8)
ax.text(1.0, 1.04, "합성 원통 · 정반사 미포함", transform=ax.transAxes,
        fontsize=6.6, color=GREY_TEXT, ha="right", va="bottom")

save_to(fig, OUT, "Fig2", DPI_LINE)
