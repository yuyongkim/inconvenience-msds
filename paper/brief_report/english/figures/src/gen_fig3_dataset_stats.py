"""Fig. 3 - Dataset characteristics, recomputed from the released JSONL.

Run gen_stats.py first; it writes fig_stats.json next to this file.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from figstyle import (FAMILY, GREY_TEXT, W_BOLD, W_XBOLD, DPI_COMBO, PAGE_W, save)

BLUE = "#2563EB"
BLUE_MID = "#7FA6F5"
BLUE_PALE = "#CFE0FF"
AMBER = "#F5A524"
RED = "#E4464B"
GREEN = "#0F9F4D"

S = json.loads((Path(__file__).with_name("fig_stats.json")).read_text(encoding="utf-8"))
cc = S["char_counts"]
total_chars = cc["korean"] + cc["latin"] + cc["digits"]
shares = [100 * cc[k] / total_chars for k in ("korean", "latin", "digits")]
lengths = np.asarray(S["hist_lengths"])
tl = S["text_len"]
n = S["n_chemicals"]

fig = plt.figure(figsize=(PAGE_W, 3.0), facecolor="white")
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.72],
                      left=0.015, right=0.985, top=0.90, bottom=0.145, wspace=0.30)

# --- (a) character-type donut -------------------------------------------------
axd = fig.add_subplot(gs[0, 0])
axd.set_title("(a) Character-type distribution (문자 종류 분포)",
              fontsize=6.6, weight=W_XBOLD, pad=6)
axd.pie(shares, colors=[BLUE, BLUE_MID, AMBER], startangle=90, counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.0))
axd.text(0, 0.10, f"{shares[0]:.1f}%", ha="center", va="center",
         fontsize=13, weight=W_XBOLD, color="#1F2937")
axd.text(0, -0.20, "Korean (한국어)", ha="center", va="center",
         fontsize=6.2, color=GREY_TEXT)
axd.set_aspect("equal")
axd.set_position([0.02, 0.30, 0.34, 0.58])

legend = [("Korean (한국어)", BLUE), ("Latin (라틴)", BLUE_MID), ("Digits (숫자)", AMBER)]
for i, (label, colour) in enumerate(legend):
    y = 0.185 - i * 0.058
    fig.patches.append(Rectangle((0.115, y), 0.019, 0.034, facecolor=colour,
                                 edgecolor="none", transform=fig.transFigure))
    fig.text(0.145, y + 0.017, label, ha="left", va="center", fontsize=6.2,
             color="#1F2937")

# --- (b) per-chemical text-length histogram -----------------------------------
axh = fig.add_subplot(gs[0, 1])
axh.set_position([0.435, 0.155, 0.545, 0.735])
bins = np.arange(0, 16000 + 100, 100)
axh.hist(lengths, bins=bins, color=BLUE_PALE, edgecolor=BLUE_MID, linewidth=0.25)
axh.set_title(f"(b) Text length per chemical (n = {n:,})",
              fontsize=6.6, weight=W_XBOLD, pad=6)

axh.axvline(tl["median"], color=GREEN, linestyle=":", linewidth=1.1)
axh.axvline(tl["mean"], color=RED, linestyle="--", linewidth=1.1)

# The two markers sit ~1,700 chars apart, so labelling them in place would
# collide; key them by colour in a block over the empty right-hand tail.
for i, (txt, colour, weight) in enumerate([
        (f"Median {tl['median']:,.0f} (중앙값)", GREEN, W_BOLD),
        (f"Mean {tl['mean']:,.0f} (평균)", RED, W_BOLD),
        (f"Std. dev. {tl['std']:,.0f} (표준편차)", "#9AA0A6", None),
        (f"Range {tl['min']:,}–{tl['max']:,} (범위)", "#9AA0A6", None)]):
    axh.text(0.985, 0.955 - i * 0.088, txt, transform=axh.transAxes,
             ha="right", va="top", fontsize=5.8, color=colour,
             **({"weight": weight} if weight else {}))

axh.set_xlabel("Korean text length per chemical, chars (텍스트 길이)", fontsize=6.2)
axh.set_ylabel("Number of chemicals (화학물질 수)", fontsize=6.2)
axh.tick_params(labelsize=5.8, length=2.2, width=0.5, colors="#5F6368")
axh.set_xlim(0, 16400)
axh.grid(axis="y", color="#EEF1F5", linewidth=0.5)
axh.set_axisbelow(True)
for side in ("top", "right"):
    axh.spines[side].set_visible(False)
for side in ("left", "bottom"):
    axh.spines[side].set_color("#DADCE0")
    axh.spines[side].set_linewidth(0.6)
axh.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")

save(fig, "Fig3", DPI_COMBO)
