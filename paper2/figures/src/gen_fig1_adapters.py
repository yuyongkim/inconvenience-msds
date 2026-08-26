"""Paper 2, Fig. 1 — where the reuse is, and where it is not.

The paper's claim is that one encoder serves catalogues that do not look alike.
A block diagram is the honest way to show it, because the claim is structural:
the wide part at the bottom is shared, the narrow parts at the top are not, and
adding a domain means adding one narrow part.

Drawn so the reader can count what a new domain costs. Everything below the
divider already exists; everything above it is what someone extending this
would write.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "paper3" / "figures" / "src"))

from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, PAGE_W, W_BOLD, save_to)

OUT = Path(__file__).resolve().parents[1]

PENDING = "#C9CDD6"

DOMAINS = [
    ("의약품\nMFDS 허가 + e약은요", "산문 · 환자용 서술", True),
    ("농약\nPSIS 등록정보", "표 · 작물×병해충", False),
    ("산업재해\nKOSHA 사례", "서술 · 자유 형식", False),
]

fig, ax = plt.subplots(figsize=(PAGE_W, 3.4))
fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")


def box(x, y, w, h, label, sub=None, face=BLUE, edge=NAVY, fs=7.4, tc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                                facecolor=face, edgecolor=edge, linewidth=0.7, zorder=3))
    ax.text(x + w / 2, y + h / 2 + (0.2 if sub else 0), label, ha="center", va="center",
            fontsize=fs, color=tc, weight=W_BOLD, zorder=4, linespacing=1.35)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.42, sub, ha="center", va="center",
                fontsize=6.2, color=tc, zorder=4, alpha=0.85)


def arrow(x, y0, y1):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>", mutation_scale=8,
                                 linewidth=0.8, color=GREY_TEXT, zorder=2))


# --- sources and adapters, one column each -------------------------------
w, gap = 2.55, 0.5
x0 = (10 - (len(DOMAINS) * w + (len(DOMAINS) - 1) * gap)) / 2
for i, (name, shape, built) in enumerate(DOMAINS):
    x = x0 + i * (w + gap)
    face = BLUE if built else PENDING
    edge = NAVY if built else "#9AA0AC"
    box(x, 8.0, w, 1.5, name, shape, face=face, edge=edge, tc="white" if built else "#31363F")
    arrow(x + w / 2, 8.0, 7.15)
    box(x, 5.9, w, 1.2, "어댑터", "읽기 순서 결정", face="#F0F2F6", edge=BORDER, tc=INK, fs=7.0)
    arrow(x + w / 2, 5.9, 4.95)
    if not built:
        ax.text(x + w / 2, 9.72, "키 신청 대기", ha="center", va="center",
                fontsize=6.0, color="#B02020", weight=W_BOLD, zorder=5)

# --- the shared floor ----------------------------------------------------
ax.plot([0.6, 9.4], [5.45, 5.45], linestyle=(0, (3, 3)), linewidth=0.7,
        color=BORDER, zorder=1)
# One caption on the line rather than two beside it: the columns reach almost
# to both margins, so anything parked at an end lands on a box.
ax.text(3.42, 5.45, "위 = 도메인마다 새로 씀   ·   아래 = 논문 1에서 그대로",
        ha="center", va="center", fontsize=6.2, color=GREY_TEXT, zorder=5,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                  edgecolor="none"))

box(1.4, 3.75, 7.2, 1.2, "공통 인코더  pipeline.ko_braille",
    "2017 한국 점자 규정 · 출처 카탈로그를 알지 못함", face=NAVY, edge=NAVY, fs=8.0)
arrow(5.0, 3.75, 2.8)
box(1.4, 1.6, 7.2, 1.2, "도메인별 검증",
    "왕복 · 규정 준수 · 팽창률 — 도메인마다 따로 보고", face="#F0F2F6",
    edge=BORDER, tc=INK, fs=7.6)

save_to(fig, OUT, "Fig1", DPI_LINE)
