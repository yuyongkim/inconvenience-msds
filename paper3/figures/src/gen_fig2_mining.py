"""Paper 3, Fig. 2 — the three failures that decide whether mining works.

Each row is a real case from the corpus, shown as what a naive method returns
and what the corrected method returns. Drawing the failures rather than the
happy path is deliberate: the method is unremarkable, and the corrections are
the contribution.
"""
import sys
from pathlib import Path

from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figbase import (BLUE, BORDER, DPI_LINE, GREY_TEXT, INK,  # noqa: E402
                     NAVY, W_BOLD, W_REG, blank_canvas, save_to)

OUT = Path(__file__).resolve().parents[1]

ROWS = [
    ("① 부분문자열 잠식", "methyl ⊃ ethyl",
     "ethyl → 틸", "ethyl → 에틸",
     "'methyl' 이름이 ethyl 양성 집합에 섞여\n공통 부분이 꼬리 한 음절로 무너진다"),
    ("② 길이 가중", "benzene",
     "benzene → 젠", "benzene → 벤젠",
     "정밀도만 보면 무관한 '다이페닐디아젠'이\n긴 형태의 점수를 깎아 짧은 쪽이 이긴다"),
    ("③ 최소 두 음절", "-ide",
     "ide → 드", "(버림)",
     "한 음절은 음차 수백 개의 끝이라\n어떤 어근도 식별하지 못한다"),
]

H = 2.75
fig, ax = blank_canvas(H)
TOP = 100 * H / 6.0

ax.text(2, TOP - 3, "채굴을 좌우하는 세 가지", fontsize=9.5, weight=W_BOLD,
        color=INK, va="top", ha="left")

ROW_H = 13.0
for i, (title, case, naive, fixed, why) in enumerate(ROWS):
    y = TOP - 11 - i * ROW_H

    ax.text(2, y + 1.6, title, fontsize=8, weight=W_BOLD, color=NAVY, va="center", ha="left")
    ax.text(2, y - 3.4, case, fontsize=7, color=GREY_TEXT, va="center",
            ha="left", family="monospace")

    # naive result
    ax.add_patch(FancyBboxPatch((23, y - 3.2), 17, 6.4, boxstyle="round,pad=0.4",
                                facecolor="#F7F7F8", edgecolor=BORDER, linewidth=0.7))
    ax.text(31.5, y, naive, fontsize=7.6, color=GREY_TEXT, va="center", ha="center")

    ax.annotate("", xy=(44.5, y), xytext=(41.5, y),
                arrowprops=dict(arrowstyle="->", color=BLUE, linewidth=1.1))

    # corrected result
    ax.add_patch(FancyBboxPatch((45.5, y - 3.2), 17, 6.4, boxstyle="round,pad=0.4",
                                facecolor="#EEF3FF", edgecolor=BLUE, linewidth=0.8))
    ax.text(54, y, fixed, fontsize=7.6, weight=W_BOLD, color=NAVY,
            va="center", ha="center")

    ax.text(64.5, y, why, fontsize=6.0, color=GREY_TEXT, va="center", ha="left",
            linespacing=1.45)

save_to(fig, OUT, "Fig2", DPI_LINE)
