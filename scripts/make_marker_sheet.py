"""A printable marker sheet, so the shoot starts with paper rather than code.

The data-collection plan says "print ArUco markers at 2 cm (the script can
generate them)". That parenthesis was doing too much work: whoever runs the
shoot would have had to find the dictionary, pick IDs, work out the DPI that
makes a marker land at exactly 20 mm on paper, and lay them out. This does it.

Physical size is the whole point. Every detection number in the paper is
stated against a marker of a known width, so a sheet that prints at 19 mm
because the printer scaled it to fit invalidates the comparison. The page is
built at true A4 dimensions with scaling off, and each marker carries its
measured width printed beside it so it can be checked with a ruler before
anything is stuck to a bottle.

The second page is the shooting grid. It is on paper because the person
holding the camera cannot read a plan on a screen at the same time, and a
condition missed in the shop cannot be recovered afterwards.

Usage:
    python scripts/make_marker_sheet.py [--size-mm 20] [--ids 0 1 2 3 4 5 6 7]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = PROJECT_ROOT / "docs" / "marker-sheet.pdf"

# The shooting grid is read in Korean, and the built-in PDF fonts carry no
# Hangul: without registering one the levels print as blank space, which is
# worse than English because it looks like the row is empty.
KO_FONTS = [
    ("KO", Path("C:/Windows/Fonts/malgun.ttf")),
    ("KO-Bold", Path("C:/Windows/Fonts/malgunbd.ttf")),
]


def register_korean() -> tuple[str, str]:
    """Return (regular, bold) font names, falling back to Helvetica."""
    try:
        for name, path in KO_FONTS:
            if not path.exists():
                raise FileNotFoundError(path)
            pdfmetrics.registerFont(TTFont(name, str(path)))
        return "KO", "KO-Bold"
    except Exception:
        print("note: no Korean font found; the grid will print in Helvetica "
              "and Hangul will be missing")
        return "Helvetica", "Helvetica-Bold"


DICT = cv2.aruco.DICT_4X4_50
PRINT_DPI = 600           # marker edges stay crisp at this size

# What varies during a sweep, printed rather than remembered.
#
# An earlier version of this sheet asked for a factorial of stills: three
# distances by five angles by two lightings by two exposures, sixty frames a
# container, 480 in all. That is the wrong medium. Two of the three artefacts
# the shoot exists to capture — motion blur and rolling shutter — occur only
# while the camera is moving, and posing for each of 480 stills removes them.
# A sweep records them for free and gives a continuous angle rather than five
# levels of one.
SWEEP = "카메라를 정면에서 70°까지 천천히 돌리며 20초 녹화 (한 번에 왕복하지 말 것)"
LIGHTING = ["실내 확산광", "직사 조명 (정반사 유도)"]
EXPOSURES = ["자동 노출", "하이라이트 기준 -2 EV"]


def marker_image(marker_id: int, px: int) -> ImageReader:
    d = cv2.aruco.getPredefinedDictionary(DICT)
    img = cv2.aruco.generateImageMarker(d, marker_id, px)
    # A quiet zone of one cell is part of the marker: without it the detector
    # has no background to find the outer border against.
    cell = px // 6
    padded = np.full((px + 2 * cell, px + 2 * cell), 255, np.uint8)
    padded[cell:cell + px, cell:cell + px] = img
    rgb = cv2.cvtColor(padded, cv2.COLOR_GRAY2RGB)
    ok, buf = cv2.imencode(".png", rgb)
    if not ok:
        raise RuntimeError(f"could not encode marker {marker_id}")
    import io as _io
    return ImageReader(_io.BytesIO(buf.tobytes()))


def draw_markers(c: canvas.Canvas, ids: list[int], size_mm: float) -> None:
    page_w, page_h = A4
    side = size_mm * mm
    quiet = side / 6.0                       # the padding added above, in points
    total = side + 2 * quiet
    px = int(round(size_mm / 25.4 * PRINT_DPI))

    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, page_h - 20 * mm, f"ArUco DICT_4X4_50 — {size_mm:.0f} mm")
    c.setFont("Helvetica", 8.5)
    c.drawString(20 * mm, page_h - 26 * mm,
                 "Print at 100%. Turn OFF 'fit to page' / 'shrink oversized pages'.")
    c.drawString(20 * mm, page_h - 30.5 * mm,
                 "Measure the black square with a ruler before use: it must read "
                 f"{size_mm:.0f} mm across.")

    cols, gap = 3, 14 * mm
    x0, y0 = 22 * mm, page_h - 48 * mm
    for i, mid in enumerate(ids):
        col, row = i % cols, i // cols
        x = x0 + col * (total + gap)
        y = y0 - row * (total + gap + 9 * mm) - total
        c.drawImage(marker_image(mid, px), x, y, width=total, height=total)

        # A ruler mark spanning exactly the black square, for checking the print.
        left, right = x + quiet, x + quiet + side
        c.setLineWidth(0.4)
        c.line(left, y - 3 * mm, right, y - 3 * mm)
        c.line(left, y - 4.5 * mm, left, y - 1.5 * mm)
        c.line(right, y - 4.5 * mm, right, y - 1.5 * mm)
        c.setFont("Helvetica", 7)
        c.drawCentredString((left + right) / 2, y - 8 * mm, f"ID {mid} · {size_mm:.0f} mm")


def draw_checklist(c: canvas.Canvas, size_mm: float, reg: str, bold: str) -> None:
    page_w, page_h = A4
    y = page_h - 22 * mm

    c.setFont(bold, 13)
    c.drawString(20 * mm, y, "촬영 조건표 · Shooting grid")
    y -= 7 * mm
    c.setFont(reg, 8.5)
    for line in [
        "Film sweeps, do not take stills. Motion blur and rolling shutter exist only while",
        "the camera moves, and they are two of the three things the synthetic study could",
        "not model. Posing for each frame removes exactly what the shoot is for.",
        "",
        "Lay the large reference marker flat beside the container, in shot throughout. It",
        "gives the camera angle for every frame — including the frames where the",
        "container's own marker is lost, which are the interesting ones. Recovering the",
        "angle from the container's marker would work only where detection worked.",
        "",
        "Note the container's diameter: it decides angle tolerance, so a sweep without it",
        "cannot be placed on the curve.",
        "",
        "Include glossy containers. Specular highlight is the factor the synthetic study",
        "could only bound, and matte-only footage would leave it exactly where it was.",
        "",
        "Film each scene at two exposures. The model predicts detection turns over on the",
        "highlight's peak brightness rather than the light's angular size, so exposure is",
        "the first prediction worth testing.",
    ]:
        c.drawString(20 * mm, y, line)
        y -= 4.6 * mm

    y -= 4 * mm
    rows = [
        ("Container", "지름 기록 · 유광/무광 구분 · 6종"),
        ("Sweep", SWEEP),
        ("Distance", "스윕 안에서 30 cm에서 1 m까지 자연스럽게 변하도록"),
        ("Lighting", " / ".join(LIGHTING)),
        ("Exposure", " / ".join(EXPOSURES)),
    ]
    c.setFont(bold, 9)
    c.drawString(20 * mm, y, "Vary")
    c.drawString(52 * mm, y, "Levels")
    y -= 3 * mm
    c.setLineWidth(0.5)
    c.line(20 * mm, y, page_w - 20 * mm, y)
    y -= 5.5 * mm
    for label, levels in rows:
        c.setFont(bold, 8.5)
        c.drawString(20 * mm, y, label)
        c.setFont(reg, 8.5)
        c.drawString(52 * mm, y, levels)
        y -= 6 * mm

    sweeps = len(LIGHTING) * len(EXPOSURES)
    y -= 3 * mm
    c.setFont(reg, 8.5)
    c.drawString(20 * mm, y,
                 f"{sweeps} sweeps per container "
                 f"({len(LIGHTING)} x {len(EXPOSURES)}), 20 seconds each. Six containers "
                 f"is {sweeps * 6 * 20 // 60} minutes of recording.")
    y -= 5 * mm
    c.drawString(20 * mm, y,
                 "At 30 fps that is about 14,000 frames — thirty times what the stills plan "
                 "would have produced,")
    y -= 4.6 * mm
    c.drawString(20 * mm, y,
                 "and it contains the blur. Drop to one lighting condition if time runs "
                 "short, but keep both exposures.")

    y -= 12 * mm
    c.setFont(bold, 10)
    c.drawString(20 * mm, y, "Record with every sweep")
    y -= 6 * mm
    c.setFont(reg, 8.5)
    for line in [
        "container ID, container diameter (mm), surface (glossy / matte),",
        f"marker ID, marker size ({size_mm:.0f} mm), lighting, exposure.",
        "",
        "Distance and angle are recovered from the footage and need not be written down.",
        "A sweep whose conditions were not written down is not a measurement.",
        "",
        "Then: python scripts/marker_video_eval.py <videos> --ref-id 0 --ref-mm 100",
    ]:
        c.drawString(20 * mm, y, line)
        y -= 4.6 * mm


def draw_reference(c: canvas.Canvas, marker_id: int, size_mm: float,
                   reg: str, bold: str) -> None:
    """The flat marker that lies beside the container and gives camera pose.

    It is large and it is on its own page because it has to stay readable at
    the angle where the container's marker is already lost. That is the whole
    point of it: the frames worth measuring are the ones where the small marker
    fails, and those frames still need an angle.
    """
    page_w, page_h = A4
    px = int(size_mm / 25.4 * PRINT_DPI)
    side = size_mm * mm
    x = (page_w - side) / 2
    y = (page_h - side) / 2 + 15 * mm
    c.drawImage(marker_image(marker_id, px), x, y, side, side)

    c.setFont(bold, 12)
    c.drawCentredString(page_w / 2, y - 12 * mm,
                        f"Reference marker · ID {marker_id} · {size_mm:.0f} mm")
    c.setFont(reg, 9)
    for i, line in enumerate([
        "용기 옆 탁자에 평평하게 놓고, 스윕 내내 화면 안에 들어오게 한다.",
        "이 마커가 모든 프레임의 카메라 각도를 준다 — 용기 마커가 놓친 프레임까지.",
        "구겨지거나 휘면 각도가 틀어지므로, 판에 붙이거나 책으로 눌러 둔다.",
    ]):
        c.drawCentredString(page_w / 2, y - (20 + 5.5 * i) * mm, line)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size-mm", type=float, default=20.0)
    ap.add_argument("--ids", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6, 7, 8],
                    help="container markers; ID 0 is reserved for the reference")
    ap.add_argument("--ref-id", type=int, default=0)
    ap.add_argument("--ref-mm", type=float, default=100.0)
    ap.add_argument("--output", default=str(OUT_PDF))
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    reg, bold = register_korean()
    c = canvas.Canvas(str(out), pagesize=A4)
    draw_markers(c, args.ids, args.size_mm)
    c.showPage()
    draw_reference(c, args.ref_id, args.ref_mm, reg, bold)
    c.showPage()
    draw_checklist(c, args.size_mm, reg, bold)
    c.showPage()
    c.save()
    print(f"-> {out}  ({len(args.ids)} container markers at {args.size_mm:.0f} mm, "
          f"reference ID {args.ref_id} at {args.ref_mm:.0f} mm, plus the shooting grid)")


if __name__ == "__main__":
    main()
