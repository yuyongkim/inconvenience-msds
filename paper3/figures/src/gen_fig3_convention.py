"""Paper 3, Fig. 3 — the roots cross the domain boundary and the spellings do not.

Two panels because the paper makes two claims that pull in opposite directions,
and a reader who sees only one of them takes away the wrong result. Left: roots
appear in both catalogues at comparable rates, so the lexicon describes
chemistry. Right: the same two elements are spelled one way by KOSHA and the
other way by the cosmetics dictionary, with nothing in between.

The zero bars on the right are the point, so they are annotated rather than
left as absent ink.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "track-a-convention-divergence.json"

d = json.loads(DATA.read_text(encoding="utf-8"))
n_kosha, n_cos = d["kosha_names"], d["cosmetic_names"]

COS_COLOR = "#E4A34A"

fig, (axl, axr) = plt.subplots(1, 2, figsize=(PAGE_W, 2.9),
                               gridspec_kw={"width_ratios": [1.0, 1.15]})
fig.subplots_adjust(left=0.105, right=0.985, top=0.78, bottom=0.20, wspace=0.50)

# ---- left: shared roots -------------------------------------------------
roots = d["shared_roots"]
labels = [r["form"] for r in roots]
x = np.arange(len(labels))
w = 0.38
axl.bar(x - w / 2, [r["kosha_pct"] * 100 for r in roots], w, color=BLUE,
        edgecolor=NAVY, linewidth=0.5, label="KOSHA 화학물질", zorder=3)
axl.bar(x + w / 2, [r["cosmetics_pct"] * 100 for r in roots], w, color=COS_COLOR,
        edgecolor="#9A6A22", linewidth=0.5, label="KCIA 화장품 성분", zorder=3)
axl.set_xticks(x)
axl.set_xticklabels(labels, fontsize=6.8, color=INK, rotation=30, ha="right")
axl.set_ylabel("이름 중 출현 비율 (%)", fontsize=7.4, color=INK)
axl.set_title("어근은 두 도메인에 함께 나타난다", fontsize=8.4, weight=W_BOLD,
              color=INK, loc="left", pad=6)
axl.legend(fontsize=6.4, frameon=False, loc="upper right")

# ---- right: element spellings -------------------------------------------
pairs = []
for e in d["elements"]:
    forms = list(e["forms"].items())
    if len(forms) == 2:
        pairs.append((e["english"], forms))
for e in d["prefixes"]:
    forms = list(e["forms"].items())
    if len(forms) == 2:
        pairs.append((e["english"], forms))

labels_r, kv, cv = [], [], []
for en, forms in pairs:
    for form, v in forms:
        labels_r.append(f"{form}  ({en})")
        kv.append(v["kosha_pct"] * 100)
        cv.append(v["cosmetics_pct"] * 100)

# Horizontal, because eight two-line labels will not fit under eight bars.
y = np.arange(len(labels_r))
axr.barh(y - w / 2, kv, w, color=BLUE, edgecolor=NAVY, linewidth=0.5,
         label="KOSHA", zorder=3)
axr.barh(y + w / 2, cv, w, color=COS_COLOR, edgecolor="#9A6A22", linewidth=0.5,
         label="KCIA", zorder=3)
for i, v in enumerate(cv):
    if v == 0:
        axr.text(0.13, i + w / 2, "0", ha="left", va="center", fontsize=6.6,
                 weight=W_BOLD, color="#B02020", zorder=5)
axr.set_yticks(y)
axr.set_yticklabels(labels_r, fontsize=6.6, color=INK)
axr.invert_yaxis()
axr.set_xlabel("이름 중 출현 비율 (%)", fontsize=7.4, color=INK)
axr.set_title("같은 원소, 다른 표기 — 관습은 전이되지 않는다", fontsize=8.4,
              weight=W_BOLD, color=INK, loc="left", pad=6)

for ax in (axl, axr):
    ax.tick_params(length=0)
    ax.grid(axis="y" if ax is axl else "x", color=BORDER, linewidth=0.5,
            alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BORDER)
axr.spines["left"].set_visible(False)

fig.text(0.985, 0.955,
         f"KOSHA n={n_kosha:,} · KCIA 표본 n={n_cos:,} · 접두사는 어두 위치만 집계",
         fontsize=6.2, color=GREY_TEXT, ha="right", va="top")

save_to(fig, OUT, "Fig3", DPI_LINE)
