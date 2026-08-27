"""Paper 2, Fig. 3 — the three catalogues really are shaped differently.

The paper claims one encoder serves documents that do not look alike. That claim
is worth nothing if the three catalogues turn out to be the same document with
different field names, so this figure is the evidence for the premise rather
than for the result.

Record length is the honest axis. A pesticide row is one approved use and stops;
a drug leaflet runs to a page and a half; an incident case is an investigator's
paragraph, and its spread is the widest of the three because some cases are one
sentence and some are a full report with a numbered preamble. The log axis is
necessary — two orders of magnitude separate the shortest pesticide row from the
longest drug leaflet — and it is what makes the overlap visible.

The expansion ratio sits beside it because it is the number an embosser cares
about, and because it moves far less than the lengths do: the shapes differ, the
cost per character barely does. That is the paper's result stated as a picture.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "paper3" / "figures" / "src"))

from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

from pipeline.adapters.drug import DrugAdapter  # noqa: E402
from pipeline.adapters.incident import IncidentAdapter  # noqa: E402
from pipeline.adapters.pesticide import PesticideAdapter  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "paper2"
VALIDATION = ROOT / "docs" / "paper2-validation.json"

DOMAINS = [
    ("drug", "의약품", "산문 · 환자용 서술", DrugAdapter),
    ("pesticide", "농약", "표 · 승인된 사용 1건", PesticideAdapter),
    ("incident", "산업재해", "서술 · 조사자 문장", IncidentAdapter),
]


def lengths(key: str, adapter_cls) -> list[int]:
    path = DATA / f"{key}_corpus.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [len(r.text()) for r in adapter_cls().adapt_many(raw.get("records", []))]


results = json.loads(VALIDATION.read_text(encoding="utf-8"))
series = [(label, sub, lengths(key, cls),
           results.get(key, {}).get("expansion_ratio", 0))
          for key, label, sub, cls in DOMAINS]

fig, (ax, ax2) = plt.subplots(
    1, 2, figsize=(PAGE_W, 3.3), gridspec_kw={"width_ratios": [2.55, 1]})
fig.subplots_adjust(left=0.175, right=0.965, top=0.86, bottom=0.185, wspace=0.30)

# --- left: length distributions ------------------------------------------
positions = list(range(len(series)))[::-1]
parts = ax.violinplot([np.log10(np.clip(v, 1, None)) for _, _, v, _ in series],
                      positions=positions, vert=False, widths=0.78,
                      showextrema=False, showmedians=False)
for body in parts["bodies"]:
    body.set_facecolor(BLUE)
    body.set_edgecolor(NAVY)
    body.set_linewidth(0.6)
    body.set_alpha(0.85)

for y, (label, sub, vals, _) in zip(positions, series):
    med = float(np.median(vals))
    ax.plot([np.log10(med)], [y], marker="o", markersize=3.4, color="white",
            markeredgecolor=NAVY, markeredgewidth=0.8, zorder=5)
    ax.text(np.log10(med), y - 0.44, f"중앙값 {med:,.0f}자  ·  n={len(vals):,}",
            ha="center", va="top", fontsize=6.4, color=GREY_TEXT, zorder=6)

ax.set_yticks(positions)
ax.set_yticklabels([f"{label}\n{sub}" for label, sub, _, _ in series],
                   fontsize=7.4, linespacing=1.5)
ticks = [1, 2, 3, 4]
ax.set_xticks(ticks)
ax.set_xticklabels(["10", "100", "1,000", "10,000"], fontsize=7)
ax.set_xlim(0.8, 4.2)
ax.set_ylim(-0.75, len(series) - 0.25)
ax.set_xlabel("레코드 하나의 길이 (자, 로그 눈금)", fontsize=7.4, color=GREY_TEXT)
ax.tick_params(axis="x", colors=GREY_TEXT, length=2)
ax.tick_params(axis="y", length=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(BORDER)
ax.grid(axis="x", color=BORDER, linewidth=0.4, alpha=0.6)
ax.set_axisbelow(True)
ax.set_title("길이는 두 자릿수 넘게 벌어진다", fontsize=8, color=INK,
             weight=W_BOLD, pad=8, loc="left")

# --- right: expansion ratio ----------------------------------------------
for y, (label, _, _, ratio) in zip(positions, series):
    ax2.barh(y, ratio, height=0.42, color=NAVY, edgecolor=NAVY, linewidth=0.6,
             zorder=3)
    ax2.text(ratio + 0.035, y, f"{ratio:.2f}", va="center", ha="left",
             fontsize=8, weight=W_BOLD, color=INK, zorder=4)

ax2.set_yticks(positions)
ax2.set_yticklabels([])
ax2.set_xlim(0, 2.25)
ax2.set_ylim(-0.75, len(series) - 0.25)
ax2.set_xticks([0, 1, 2])
ax2.set_xlabel("글자당 점자 칸 수", fontsize=7.4, color=GREY_TEXT)
ax2.tick_params(axis="x", labelsize=7, colors=GREY_TEXT, length=2)
ax2.tick_params(axis="y", length=0)
for side in ("top", "right", "left"):
    ax2.spines[side].set_visible(False)
ax2.spines["bottom"].set_color(BORDER)
ax2.grid(axis="x", color=BORDER, linewidth=0.4, alpha=0.6)
ax2.set_axisbelow(True)
ax2.set_title("점역 비용은 거의 같다", fontsize=8, color=INK, weight=W_BOLD,
              pad=8, loc="left")

save_to(fig, OUT, "Fig3", DPI_LINE)
