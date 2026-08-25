"""Paper 5, Fig. 2 — the column that would make the split possible is not there.

Figure 1 shows the two splits disagreeing on synthetic data, which is an
argument about method. This one is an argument about data, and it needs to be
seen rather than read: a grid of what the public sign-alphabet datasets
actually store, with the signer column empty all the way down.

The empty column is the figure. Everything else is context for it, so the
present cells are drawn quietly and only the absence is marked.
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
DATA = ROOT / "docs" / "track-c-dataset-audit.json"

raw = json.loads(DATA.read_text(encoding="utf-8"))
rows = [r for r in raw["datasets"] if r["columns"]]

# Three things a person-independent split needs: the sample, its letter, and
# who made it. The first two are always present; the third never is.
COLS = [
    ("표본\n(image/video)", lambda c: any(x in c for x in ("image", "video"))),
    ("레이블\n(label)", lambda c: "label" in c),
    ("화자 식별자\n(signer)", lambda c: False),
]

present = np.array([[int(test(r["columns"])) for _, test in COLS] for r in rows])

# Four of these repositories are named "American-Sign-Language-Dataset", so the
# bare name identifies nothing. The owner is what tells them apart.
labels = []
for r in rows:
    owner, name = r["dataset"].split("/", 1)
    short = name.replace("American-Sign-Language", "ASL").replace("_Rencoded", "")
    if len(short) > 30:
        short = short[:29] + "…"
    labels.append(f"{owner}/{short}")

fig, ax = plt.subplots(figsize=(PAGE_W, 2.9))
fig.subplots_adjust(left=0.415, right=0.985, top=0.74, bottom=0.06)

for i in range(len(rows)):
    for j in range(len(COLS)):
        if present[i, j]:
            ax.add_patch(plt.Rectangle((j - 0.42, i - 0.36), 0.84, 0.72,
                                       facecolor=BLUE, edgecolor=NAVY,
                                       linewidth=0.5, zorder=3))
            ax.text(j, i, "있음", ha="center", va="center", fontsize=6.6,
                    color="white", zorder=4)
        else:
            ax.add_patch(plt.Rectangle((j - 0.42, i - 0.36), 0.84, 0.72,
                                       facecolor="#FBEDED", edgecolor="#DDAAAA",
                                       linewidth=0.5, linestyle=(0, (2, 2)), zorder=3))
            ax.text(j, i, "없음", ha="center", va="center", fontsize=6.6,
                    weight=W_BOLD, color="#B02020", zorder=4)

ax.set_xlim(-0.6, len(COLS) - 0.4)
ax.set_ylim(len(rows) - 0.5, -0.5)
ax.set_xticks(range(len(COLS)))
ax.set_xticklabels([c[0] for c in COLS], fontsize=7, color=INK)
ax.xaxis.set_ticks_position("top")
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(labels, fontsize=6.4, color=INK)
ax.tick_params(length=0)
for side in ("top", "right", "left", "bottom"):
    ax.spines[side].set_visible(False)

ax.set_title("공개 지문자 데이터셋이 기록하는 것", fontsize=9, weight=W_BOLD,
             color=INK, loc="left", pad=26, x=-0.72)
fig.text(0.985, 0.965,
         f"Hugging Face datasets API · 조회 {len(raw['datasets'])}종 중 "
         f"스키마 확인 {raw['resolved']}종 · 화자 필드 보유 {raw['with_signer_field']}종",
         fontsize=6.2, color=GREY_TEXT, ha="right", va="top")

save_to(fig, OUT, "Fig2", DPI_LINE)
