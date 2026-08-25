"""Figure style for the follow-up papers.

Reuses the published paper's palette and font stack so the series looks like one
body of work, but saves into the calling paper's own figures directory.

The published `figstyle.save` resolves its output path from its own file
location, so importing it from another paper writes over paper 1's figures. That
happened once. `save_to` takes the directory explicitly.
"""
from pathlib import Path
import sys

_P1_SRC = Path(__file__).resolve().parents[3] / "paper" / "brief_report" / "english" / "figures" / "src"
sys.path.insert(0, str(_P1_SRC))

from figstyle import (  # noqa: E402,F401
    BLUE, BLUE_PALE, BLUE_UI, BORDER, DPI_COMBO, DPI_LINE, FAMILY, GREY_BG,
    GREY_TEXT, INK, JAMO_BLUE, NAVY, PAGE_W, W_BOLD, W_HEAVY, W_LIGHT, W_REG,
    W_XBOLD, blank_canvas,
)

import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402


def save_to(fig, out_dir: Path, stem: str, dpi: int) -> None:
    """Write <stem>.png and <stem>.pdf into out_dir."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{stem}.png"
    pdf = out_dir / f"{stem}.pdf"
    fig.savefig(png, dpi=dpi, facecolor=fig.get_facecolor())
    fig.savefig(pdf, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Flatten onto white: an alpha channel prints as a black box on some RIPs.
    img = Image.open(png)
    if img.mode in ("RGBA", "LA"):
        flat = Image.new("RGB", img.size, "white")
        flat.paste(img, mask=img.split()[-1])
        flat.save(png)
        img = flat
    print(f"wrote {png} [{img.mode} {img.width}x{img.height}, {dpi} dpi]")
