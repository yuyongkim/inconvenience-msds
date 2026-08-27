"""Fig. 1 - System architecture (acquisition -> extraction -> encoding -> delivery -> access)."""
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrow

from figstyle import (BLUE, BLUE_PALE, BORDER, GREY_TEXT, NAVY, W_BOLD, W_XBOLD,
                      DPI_LINE, blank_canvas, save)

STAGES = [
    ("KOSHA API", "Acquisition", True),
    ("XML Parsing\n& GHS Conv.", "Extraction", False),
    ("Korean Braille\nEncoder", "Encoding", False),
    ("Web Service", "Delivery", False),
    ("User Browser", "Access", True),
]

H_IN = 1.30
fig, ax = blank_canvas(H_IN)
TOP = 100 * H_IN / 6.0            # axes height in local units

BOX_W, BOX_H = 16.6, 9.6
GAP = (100 - 5 * BOX_W) / 4.0
BOX_Y = TOP - 2.0 - BOX_H

for i, (label, stage, filled) in enumerate(STAGES):
    x = i * (BOX_W + GAP)
    ax.add_patch(FancyBboxPatch(
        (x, BOX_Y), BOX_W, BOX_H,
        boxstyle="round,pad=0,rounding_size=1.2",
        linewidth=0.7,
        facecolor=NAVY if filled else "white",
        edgecolor=NAVY if filled else BORDER,
        zorder=2))
    ax.text(x + BOX_W / 2, BOX_Y + BOX_H / 2, label,
            ha="center", va="center", fontsize=7.2, weight=W_XBOLD,
            color="white" if filled else NAVY, linespacing=1.45, zorder=3)

    if i < len(STAGES) - 1:
        ax.add_patch(FancyArrow(
            x + BOX_W + GAP * 0.20, BOX_Y + BOX_H / 2, GAP * 0.60, 0,
            width=0.38, head_width=1.45, head_length=1.25,
            length_includes_head=True, color=BLUE, zorder=3))

    cy = BOX_Y - 3.2
    ax.add_patch(Circle((x + BOX_W / 2, cy), 1.75,
                        facecolor=NAVY if filled else BLUE_PALE,
                        edgecolor="none", zorder=3))
    ax.text(x + BOX_W / 2, cy, str(i + 1), ha="center", va="center",
            fontsize=5.6, weight=W_XBOLD,
            color="white" if filled else BLUE, zorder=4)
    ax.text(x + BOX_W / 2, cy - 4.6, stage, ha="center", va="center",
            fontsize=6.2, color=GREY_TEXT, zorder=3)

save(fig, "Fig1", DPI_LINE)
