"""What a glossy container does to marker detection.

The cylinder study closed the curvature gap and left one modelled factor
open: cosmetics packaging is mostly glossy, and a glossy cylinder under a
point light shows a bright vertical band where the surface normal bisects the
light and the camera. Inside that band the sensor clips, and clipped pixels
carry no black-and-white pattern for the detector to read.

This is still synthetic and does not replace photographs. What it can do is
say which parameter the photographs need to vary. If detection turns out to
depend on how wide the highlight is rather than how bright it is, then the
useful thing to control in a real shoot is the light source's angular size,
not its power, and that is worth knowing before the shoot rather than after.

The model is deliberately plain: a Blinn-Phong specular lobe on the cylinder,
added to the marker and clipped at 255 the way a sensor clips. Its shininess
exponent sets the band's width and its coefficient sets the peak. Real
packaging adds coating texture, coloured light and inter-reflection, none of
which is here.

Usage:
    python scripts/marker_specular.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.path.insert(0, str(Path(__file__).resolve().parent))
from marker_cylinder import wrap_on_cylinder  # noqa: E402
from marker_feasibility import DICT, FRAME, MARKER_ID, degrade, render_marker  # noqa: E402

OUT_JSON = PROJECT_ROOT / "docs" / "track-b-specular-measurements.json"
TRIALS = 12

# Shininess exponents, and the highlight width each produces on the marker.
# Low exponent spreads the lobe over most of the visible arc; high exponent
# concentrates it into a narrow strip.
SHININESS = [8, 24, 64, 200]

# Peak specular strength, in units of the 0-255 sensor range. 0 is matte.
# The lobe peaks at cos(0)**n = 1 whatever the exponent, so the brightest
# column always receives the full strength and the grid is dense where
# detection turns over rather than spread evenly.
STRENGTH = [0, 60, 100, 130, 150, 170, 190, 210, 230, 255]

# Container curvatures carried over from the cylinder study.
WRAPS = [0.10, 0.20]


def specular_band(shape: tuple[int, int], wrap: float, angle_deg: float,
                  shininess: int, strength: float, light_deg: float = 20.0) -> np.ndarray:
    """A Blinn-Phong highlight across the visible arc of the cylinder.

    Every output column corresponds to a surface angle, so the lobe is a
    function of column alone: the band runs vertically, which is what a
    highlight on an upright bottle does.
    """
    h, w = shape
    if strength <= 0 or w < 2:
        return np.zeros(shape, np.float32)

    half = np.pi * max(wrap, 1e-6)
    view = np.radians(angle_deg)
    light = np.radians(light_deg)

    # Surface angle per output column, over the arc actually facing the camera.
    thetas = view + (np.arange(w) / (w - 1) - 0.5) * 2 * half
    # Halfway vector between view and light directions, in the same angle space.
    halfway = (view + light) / 2.0
    lobe = np.cos(np.clip(thetas - halfway, -np.pi / 2, np.pi / 2)) ** shininess
    band = (strength * lobe).astype(np.float32)
    return np.tile(band, (h, 1))


def scene_with_highlight(marker: np.ndarray, wrap: float, angle_deg: float,
                         shininess: int, strength: float) -> np.ndarray:
    scene = wrap_on_cylinder(marker, wrap, angle_deg)
    # The highlight lives on the marker patch, not on the whole frame.
    ys, xs = np.where(scene != 210)
    if ys.size == 0:
        return scene
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    patch = scene[y0:y1, x0:x1].astype(np.float32)
    patch += specular_band(patch.shape, wrap, angle_deg, shininess, strength)
    scene[y0:y1, x0:x1] = np.clip(patch, 0, 255).astype(np.uint8)
    return scene


def contrast_after(marker: np.ndarray, wrap: float, angle_deg: float,
                   shininess: int, strength: float) -> tuple[float, float]:
    """Whole-marker and worst-column black/white separation after the highlight.

    Counting saturated columns turned out to measure the marker's own white
    border rather than the highlight. The mean separation is better but still
    misleading, because it lets a narrow lobe hide: a highlight that erases one
    strip of the marker barely moves the average.

    So the second number is the worst column. The detector has to read every
    cell, so the strip where black and white have collapsed into each other is
    what decides the outcome, not the marker's average.

    Returns (mean separation, minimum separation over columns).
    """
    plain = wrap_on_cylinder(marker, wrap, angle_deg)
    lit = scene_with_highlight(marker, wrap, angle_deg, shininess, strength)
    ys, xs = np.where(plain != 210)
    if ys.size == 0:
        return 0.0, 0.0
    box = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    base, now = plain[box].astype(np.float32), lit[box].astype(np.float32)
    dark, light = base < 128, base >= 128
    if not dark.any() or not light.any():
        return 0.0, 0.0
    mean_sep = float(now[light].mean() - now[dark].mean())

    worst = np.inf
    for c in range(base.shape[1]):
        d, l = dark[:, c], light[:, c]
        if d.any() and l.any():
            worst = min(worst, float(now[l, c].mean() - now[d, c].mean()))
    return mean_sep, (0.0 if worst is np.inf else worst)


def core_width_cells(wrap: float, shininess: int, cells_across: int = 6) -> float:
    """Width of the highlight's bright core, in marker cells.

    The peak of the lobe is 1 whatever the exponent, so peak brightness alone
    cannot separate a wide wash from a thin line. This measures the half-power
    width instead and expresses it in the unit the detector works in, which is
    the marker cell: a 4x4 dictionary marker is six cells across counting its
    border.
    """
    half = np.pi * max(wrap, 1e-6)                 # half the arc the marker spans
    d = float(np.arccos(0.5 ** (1.0 / shininess)))  # angle where the lobe halves
    return (2 * d) / (2 * half) * cells_across


def detect(scene: np.ndarray) -> bool:
    det = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(DICT), cv2.aruco.DetectorParameters()
    )
    _, ids, _ = det.detectMarkers(scene)
    return ids is not None and MARKER_ID in ids.flatten()


def main() -> None:
    px = 120
    marker = render_marker(px)
    angle = 0.0                      # head-on, the case curvature does not spoil

    rows = []
    print(f"OpenCV {cv2.__version__}, marker {px}px, {TRIALS} trials per cell")
    print("Head-on view; specular lobe from a light 20 degrees off the camera axis.\n")

    for wrap in WRAPS:
        print(f"wrap {wrap:.2f}")
        print("  shininess  " + "".join(f"{s:>7}" for s in STRENGTH))
        for sh in SHININESS:
            cells, lifts, seps = [], [], []
            for st in STRENGTH:
                rng = np.random.default_rng(int(wrap * 100) * 977 + sh * 31 + int(st))
                hits = sum(
                    detect(degrade(
                        scene_with_highlight(marker, wrap, angle, sh, float(st)), rng))
                    for _ in range(TRIALS)
                )
                mean_sep, worst_sep = contrast_after(marker, wrap, angle, sh, float(st))
                cells.append(hits)
                lifts.append(mean_sep)
                seps.append(worst_sep)
                rows.append({"wrap": wrap, "shininess": sh, "strength": st,
                             "detected": hits, "trials": TRIALS,
                             "mean_separation": round(mean_sep, 1),
                             "worst_column_separation": round(worst_sep, 1)})
            bar = "".join(f"{c / TRIALS:>7.0%}" for c in cells)
            last_ok = max((st for st, c in zip(STRENGTH, cells) if c == TRIALS),
                          default=None)
            core = core_width_cells(wrap, sh)
            print(f"  {sh:>9}  {bar}   holds to {last_ok}, core {core:.2f} cells")
            for r in rows[-len(STRENGTH):]:
                r["core_width_cells"] = round(core, 3)
                r["highest_strength_fully_detected"] = last_ok
            print(f"  {'':>9}  " + "".join(f"{v:>7.0f}" for v in seps) + "   <- worst column")
        print()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "note": "Synthetic Blinn-Phong highlight on a cylinder. Not photographs.",
        "opencv": cv2.__version__,
        "marker_px": px,
        "angle_deg": angle,
        "light_offset_deg": 20.0,
        "trials_per_condition": TRIALS,
        "grid": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {OUT_JSON}")


if __name__ == "__main__":
    main()
