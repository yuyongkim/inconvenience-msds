"""Paper 2, Fig. 2 — why the obvious round-trip number is the wrong one.

The naive check is encode, decode, compare against the source. Read that way the
pesticide domain scores 9.5% and looks broken. It is not broken: 제38항 [다만]
requires a space between a digit and an initial that shares its cell, so a
사용횟수 of "3회" must be embossed as "3 회", and no decoder can put the space
back. The score is measuring the writing system.

The pairs below are drawn side by side so the gap is the subject of the figure
rather than a caveat under it. The dark bar is the fixed-point test — encode and
decode twice, and ask whether the second pass changed anything — which is what
actually answers "did the pipeline lose something".

The pesticide gap is the widest because its rows are short and almost all carry
a 사용횟수; the drug and incident gaps are narrower because a long record has
more places to be right in.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "paper3" / "figures" / "src"))

from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "paper2-validation.json"

LABELS = {
    "drug": "의약품\nMFDS 허가 + e약은요",
    "pesticide": "농약\n식품안전나라 등록정보",
    "incident": "산업재해\nKOSHA 재해사례",
}

results = json.loads(DATA.read_text(encoding="utf-8"))
domains = [k for k in ("drug", "pesticide", "incident") if k in results]

fig, ax = plt.subplots(figsize=(PAGE_W, 3.5))
fig.subplots_adjust(left=0.20, right=0.965, top=0.80, bottom=0.13)

H = 0.30
for i, key in enumerate(domains):
    r = results[key]
    exact = r["roundtrip_exact_pct"] * 100
    stable = r["roundtrip_stable_pct"] * 100
    y = len(domains) - 1 - i

    ax.barh(y + H / 2 + 0.02, exact, height=H, color="#C9D6F0",
            edgecolor=NAVY, linewidth=0.6, zorder=3)
    ax.barh(y - H / 2 - 0.02, stable, height=H, color=NAVY,
            edgecolor=NAVY, linewidth=0.6, zorder=3)

    ax.text(exact + 1.4, y + H / 2 + 0.02, f"{exact:.1f}%", va="center",
            ha="left", fontsize=8, color=INK, zorder=4)
    ax.text(stable + 1.4, y - H / 2 - 0.02, f"{stable:.1f}%", va="center",
            ha="left", fontsize=8, weight=W_BOLD, color=INK, zorder=4)

    # The gap is the claim, so it gets a bracket rather than a caption.
    if stable - exact > 8:
        ax.annotate("", xy=(exact, y), xytext=(stable, y),
                    arrowprops=dict(arrowstyle="<->", linewidth=0.7,
                                    color=GREY_TEXT, shrinkA=0, shrinkB=0),
                    zorder=5)
        ax.text((exact + stable) / 2, y + 0.005,
                f"규정이 만든 차이  {stable - exact:.0f}%p",
                ha="center", va="bottom", fontsize=6.4, color=GREY_TEXT,
                zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="none"))

ax.set_yticks(range(len(domains)))
ax.set_yticklabels([LABELS[k] for k in reversed(domains)], fontsize=7.6,
                   linespacing=1.5)
ax.set_xlim(0, 108)
ax.set_ylim(-0.62, len(domains) - 0.38)
ax.set_xlabel("원문과 일치한 레코드 비율 (%)", fontsize=7.6, color=GREY_TEXT)
ax.tick_params(axis="x", labelsize=7, colors=GREY_TEXT, length=2)
ax.tick_params(axis="y", length=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(BORDER)
ax.grid(axis="x", color=BORDER, linewidth=0.4, alpha=0.6, zorder=0)
ax.set_axisbelow(True)

handles = [
    plt.Rectangle((0, 0), 1, 1, facecolor="#C9D6F0", edgecolor=NAVY, linewidth=0.6),
    plt.Rectangle((0, 0), 1, 1, facecolor=NAVY, edgecolor=NAVY, linewidth=0.6),
]
ax.legend(handles,
          ["원문 그대로 일치 — 규정이 넣은 빈칸까지 오류로 셈",
           "고정점 도달 — 두 번째 왕복에서 더 잃는 것이 없음"],
          loc="upper left", bbox_to_anchor=(-0.245, 1.17), ncol=1,
          frameon=False, fontsize=6.9, handlelength=1.1, handleheight=0.9,
          labelspacing=0.35)

save_to(fig, OUT, "Fig2", DPI_LINE)
