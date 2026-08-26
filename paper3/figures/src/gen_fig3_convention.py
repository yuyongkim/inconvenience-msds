"""Paper 3, Fig. 3 — the roots cross the registry boundary and the spellings do not.

Two panels because the paper makes two claims that pull in opposite directions,
and a reader who sees only one of them takes away the wrong result. Left: the
shared chemical roots appear in all three catalogues, so the lexicon describes
chemistry. Right: the same two elements are spelled one way by pharmacy and the
other by cosmetics with nothing in between, and KOSHA — the registry this
project mined its lexicon from — is the only one that uses both.

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
n_kosha = d["kosha_names"]
n_cos = d["cosmetic_names"]
n_drug = d.get("drug_names", 0)

# Three registries, three colours. KOSHA keeps the blue it carries in Fig. 1;
# the two it is compared against are warm, so the eye reads them as a pair
# standing against it.
SERIES = [
    ("kosha_pct", BLUE, NAVY, f"KOSHA 화학물질 (n={n_kosha:,})"),
    ("drugs_pct", "#C05A4A", "#7E3125", f"MFDS 의약품 성분 (n={n_drug:,})"),
    ("cosmetics_pct", "#E4A34A", "#9A6A22", f"KCIA 화장품 성분 (n={n_cos:,})"),
]

fig, (axl, axr) = plt.subplots(1, 2, figsize=(PAGE_W, 3.1),
                               gridspec_kw={"width_ratios": [1.0, 1.2]})
fig.subplots_adjust(left=0.105, right=0.985, top=0.76, bottom=0.21, wspace=0.52)

# ---- left: shared roots -------------------------------------------------
roots = d["shared_roots"]
labels = [r["form"] for r in roots]
x = np.arange(len(labels))
w = 0.26
for i, (key, face, edge, label) in enumerate(SERIES):
    axl.bar(x + (i - 1) * w, [r.get(key, 0) * 100 for r in roots], w,
            color=face, edgecolor=edge, linewidth=0.45, label=label, zorder=3)
axl.set_xticks(x)
axl.set_xticklabels(labels, fontsize=6.6, color=INK, rotation=30, ha="right")
axl.set_ylabel("이름 중 출현 비율 (%)", fontsize=7.4, color=INK)
axl.set_title("어근은 세 등록부에 함께 나타난다", fontsize=8.4, weight=W_BOLD,
              color=INK, loc="left", pad=6)
axl.legend(fontsize=5.8, frameon=False, loc="upper right")

# ---- right: element and prefix spellings --------------------------------
pairs = []
for e in d["elements"] + d["prefixes"]:
    forms = list(e["forms"].items())
    if len(forms) == 2:
        pairs.append((e["english"], forms))

labels_r = []
vals = {key: [] for key, _, _, _ in SERIES}
for en, forms in pairs:
    for form, v in forms:
        labels_r.append(f"{form}  ({en})")
        for key, _, _, _ in SERIES:
            vals[key].append(v.get(key, 0) * 100)

# Horizontal, because eight two-part labels will not fit under eight bars.
y = np.arange(len(labels_r))
for i, (key, face, edge, _) in enumerate(SERIES):
    axr.barh(y + (i - 1) * w, vals[key], w, color=face, edgecolor=edge,
             linewidth=0.45, zorder=3)

# A registry that never writes a form its neighbour writes constantly has a
# house style rather than a preference, so the zeros are labelled.
for i in range(len(labels_r)):
    for j, (key, _, _, _) in enumerate(SERIES):
        if vals[key][i] == 0:
            axr.text(0.1, i + (j - 1) * w, "0", ha="left", va="center",
                     fontsize=5.6, weight=W_BOLD, color="#B02020", zorder=5)

axr.set_yticks(y)
axr.set_yticklabels(labels_r, fontsize=6.4, color=INK)
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

fig.text(0.985, 0.965, "접두사는 어두 위치만 집계",
         fontsize=6.2, color=GREY_TEXT, ha="right", va="top")

save_to(fig, OUT, "Fig3", DPI_LINE)
