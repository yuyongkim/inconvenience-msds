"""Fig. 5 - Reference web deployment.

The braille column is produced by the released encoder, not typeset by hand.
"""
import sys
from pathlib import Path

import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from pipeline.ko_braille import encode_korean_braille  # noqa: E402

from figstyle import (BLUE_PALE_UI, BLUE_UI, GREY_BG, W_BOLD, W_XBOLD,  # noqa: E402
                      DPI_LINE, blank_canvas, save)

fm.fontManager.addfont(r"C:\Windows\Fonts\seguisym.ttf")
BRAILLE_FONT = "Segoe UI Symbol"

SRC_W, SRC_H = 901.0, 607.0          # geometry taken from the live screenshot
H_IN = 6.0 * SRC_H / SRC_W
fig, ax = blank_canvas(H_IN)

INK = "#3C4043"
MUTED = "#80868B"
LINE = "#E3E5E8"


def X(px):
    return px / SRC_W * 100.0


def Y(py):
    return (SRC_H - py) / SRC_W * 100.0


def box(x0, y0, x1, y1, fc, ec=None, r=0.0, lw=0.6, z=2):
    ax.add_patch(FancyBboxPatch(
        (X(x0), Y(y1)), X(x1) - X(x0), Y(y0) - Y(y1),
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=fc, edgecolor=ec or fc, linewidth=lw, zorder=z))


def txt(px, py, s, size=5.4, color=INK, ha="left", weight=None, font=None, z=4):
    kw = {}
    if weight:
        kw["weight"] = weight
    if font:
        kw["fontname"] = font
    ax.text(X(px), Y(py), s, fontsize=size, color=color, ha=ha, va="center",
            zorder=z, **kw)


box(18, 10, 884, 600, GREY_BG, "#ECECEC", r=0.6, lw=0.5, z=1)          # page
box(40, 47, 862, 105, BLUE_UI, r=0.8, z=2)                              # header
txt(451, 76, "MSDS 점자 변환", size=8.0, color="white", ha="center",
    weight=W_BOLD)

box(200, 122, 710, 168, "white", "#DFE1E5", r=0.6, z=2)                 # search
txt(216, 145, "벤젠", size=5.6)
box(637, 127, 703, 163, BLUE_UI, r=0.5, z=3)
txt(670, 145, "검색", size=4.8, color="white", ha="center", weight=W_BOLD, z=4)

box(45, 181, 297, 580, "white", "#E6E8EB", r=0.6, z=2)                  # list card
box(306, 181, 857, 580, "white", "#E6E8EB", r=0.6, z=2)                 # detail card

txt(171, 205, "화학물질 목록", size=5.6, ha="center", weight=W_BOLD)
CHEMICALS = ["벤젠 (Benzene)", "톨루엔 (Toluene)", "아세톤 (Acetone)",
             "메탄올 (Methanol)", "에탄올 (Ethanol)", "자일렌 (Xylene)",
             "포름알데히드 (Formaldehyde)"]
for i, name in enumerate(CHEMICALS):
    cy = 236 + i * 41.8
    if i == 0:
        box(58, cy - 16, 284, cy + 16, BLUE_PALE_UI, r=0.4, z=3)
    txt(70, cy, name, size=4.9, color=BLUE_UI if i == 0 else MUTED,
        weight=W_BOLD if i == 0 else None)

txt(581, 205, "벤젠 – 상세 정보", size=5.6, ha="center", weight=W_BOLD)
ax.plot([X(330), X(833)], [Y(228), Y(228)], color=LINE, linewidth=0.5, zorder=3)
txt(450, 252, "한국어 텍스트", size=5.0, color=BLUE_UI, ha="center", weight=W_BOLD)
txt(716, 252, "점자 변환", size=5.0, color=BLUE_UI, ha="center", weight=W_BOLD)
ax.plot([X(583), X(583)], [Y(270), Y(556)], color=LINE, linewidth=0.5, zorder=3)

ROWS = ["물질명: 벤젠",
        "분자식: C6H6",
        "CAS 번호: 71-43-2",
        "유해성: 발암성 물질",
        "취급 주의사항:",
        "  - 흡입 시 신선한 공기로 이동",
        "  - 피부 접촉 시 물로 세척",
        "  - 화기 엄금"]
for i, row in enumerate(ROWS):
    ry = 288 + i * 34.6
    txt(340, ry, row.replace("C6H6", "C\u2086H\u2086"), size=4.7)
    txt(600, ry, encode_korean_braille(row.strip()), size=4.1,
        font=BRAILLE_FONT)

save(fig, "Fig5", DPI_LINE)
