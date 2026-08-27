"""Shared style for the brief-report figures.

Every figure is laid out at its final print width (6.0 in, the manuscript text
width) so that point sizes in the source are the point sizes on the page, and
rendered at Springer's line-art / combination-art resolution.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

FONT_DIR = Path(r"C:\Users\USER\AppData\Local\Microsoft\Windows\Fonts")
_FACES = ["NanumSquareNeo-aLt.ttf", "NanumSquareNeo-bRg.ttf",
          "NanumSquareNeo-cBd.ttf", "NanumSquareNeo-dEb.ttf",
          "NanumSquareNeo-eHv.ttf"]
for _f in _FACES:
    fm.fontManager.addfont(str(FONT_DIR / _f))

FAMILY = fm.FontProperties(fname=str(FONT_DIR / "NanumSquareNeo-bRg.ttf")).get_name()

# NanumSquareNeo ships its five faces as separate weights of one family;
# matplotlib maps them onto the standard weight ladder.
W_LIGHT, W_REG, W_BOLD, W_XBOLD, W_HEAVY = 350, 400, 700, 800, 900

NAVY = "#14213D"
BLUE = "#2563EB"
BLUE_UI = "#1A73E8"
BLUE_PALE = "#EEF3FF"
BLUE_PALE_UI = "#E8F0FE"
JAMO_BLUE = "#1766C0"
BORDER = "#D5DCE9"
GREY_TEXT = "#8A8F98"
GREY_BG = "#F5F5F5"
INK = "#222222"

PAGE_W = 6.0          # manuscript text width, inches
DPI_LINE = 1000       # Springer: line art
DPI_COMBO = 600       # Springer: combination (line + halftone/greys)

plt.rcParams.update({
    "font.family": FAMILY,
    "axes.unicode_minus": False,
    "svg.fonttype": "path",
    "pdf.fonttype": 42,
})


def blank_canvas(height_in, facecolor="white"):
    """A 6.0 in wide figure with a single 0-100 x 0-100 drawing axes."""
    fig = plt.figure(figsize=(PAGE_W, height_in), facecolor=facecolor)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * height_in / PAGE_W)
    ax.set_axis_off()
    ax.set_facecolor(facecolor)
    return fig, ax


def save(fig, stem, dpi):
    out_dir = Path(__file__).resolve().parent.parent
    png = out_dir / f"{stem}.png"
    pdf = out_dir / f"{stem}.pdf"
    fig.savefig(png, dpi=dpi, facecolor=fig.get_facecolor())
    fig.savefig(pdf, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Flatten onto white: matplotlib always emits RGBA, and an alpha channel can
    # print as a black box on some publisher RIPs.
    from PIL import Image
    im = Image.open(png)
    if im.mode in ("RGBA", "LA", "P"):
        rgba = im.convert("RGBA")
        flat = Image.new("RGB", rgba.size, (255, 255, 255))
        flat.paste(rgba, (0, 0), rgba)
        flat.save(png, dpi=(dpi, dpi))
        im = flat
    print(f"wrote {png} [{im.mode} {im.size[0]}x{im.size[1]}, {dpi} dpi "
          f"at {PAGE_W} in wide] and {pdf}")
