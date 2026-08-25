"""Detection on a curved surface, which is what cosmetics packaging actually is.

The planar measurement in `marker_feasibility.py` is the optimistic case. A
marker wrapped around a bottle is not a plane seen at an angle: the further from
the centre line, the more the surface turns away, so the marker's own squares
compress unevenly across its width. A homography cannot express that.

This wraps the marker onto a cylinder of a given radius and re-measures. The
free parameter that matters is the ratio of marker width to bottle
circumference: a 2 cm marker on a wide jar is nearly flat, and the same marker
on a lip-balm tube is not.

Still synthetic, still no specular highlight — glossy packaging remains
untested. But curvature is the largest modelled gap and this closes it.

Usage:
    python scripts/marker_cylinder.py
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
from marker_feasibility import DICT, FRAME, MARKER_ID, degrade, render_marker  # noqa: E402

OUT_JSON = PROJECT_ROOT / "docs" / "track-b-cylinder-measurements.json"
TRIALS = 12

# Marker width as a fraction of the container's circumference. 0.0 is flat;
# 0.5 means the marker wraps half way round, which no real label would do.
WRAP_FRACTIONS = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50]

# Typical containers, for reading the wrap fraction back into something physical.
CONTAINERS = {
    "wide jar (d=70mm)": 0.09,      # 20mm marker / 220mm circumference
    "cream tube (d=40mm)": 0.16,
    "serum bottle (d=30mm)": 0.21,
    "lip balm (d=16mm)": 0.40,
}


def wrap_on_cylinder(marker: np.ndarray, wrap: float, angle_deg: float) -> np.ndarray:
    """Project a flat marker onto a cylinder and render it from `angle_deg`.

    Each column of the marker sits at an angle theta around the cylinder. Its
    horizontal position projects as sin(theta) and its visibility as cos(theta),
    so columns near the silhouette compress toward nothing — the effect a
    perspective warp cannot produce.
    """
    h, w = FRAME
    scene = np.full((h, w), 210, np.uint8)
    mh, mw = marker.shape

    if wrap <= 1e-6:
        # Flat case: a plain rotation about the vertical axis.
        t = np.radians(angle_deg)
        out = cv2.resize(marker, (max(int(mw * abs(np.cos(t))), 1), mh))
    else:
        half = np.pi * wrap                       # half the arc the marker covers
        view = np.radians(angle_deg)

        # Angular extent that is still facing the camera.
        thetas = (np.arange(mw) / (mw - 1) - 0.5) * 2 * half + view
        visible = np.cos(thetas) > 0.02
        if visible.sum() < 8:
            return scene
        sins = np.sin(thetas[visible])
        lo, hi = sins.min(), sins.max()

        # Sample per OUTPUT column. Mapping forward from source columns leaves
        # unwritten gaps in the output, which read as stripes through the marker
        # and break detection for reasons that have nothing to do with curvature.
        width = max(int(mw * (hi - lo) / (2 * np.sin(half))), 1)
        us = lo + (np.arange(width) / max(width - 1, 1)) * (hi - lo)
        src_theta = np.arcsin(np.clip(us, -1, 1))
        # arcsin returns the near-side solution; shift back into marker coords.
        src_x = ((src_theta - view) / (2 * half) + 0.5) * (mw - 1)
        src_x = np.clip(np.round(src_x).astype(int), 0, mw - 1)
        out = marker[:, src_x]

    oh, ow = out.shape
    y, x0 = (h - oh) // 2, (w - ow) // 2
    if oh > h or ow > w:
        return scene
    scene[y : y + oh, x0 : x0 + ow] = out
    return scene


def detect(scene: np.ndarray) -> bool:
    det = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(DICT), cv2.aruco.DetectorParameters()
    )
    _, ids, _ = det.detectMarkers(scene)
    return ids is not None and MARKER_ID in ids.flatten()


def main() -> None:
    px = 120                                     # comfortably above the planar floor
    marker = render_marker(px)
    angles = [0, 15, 30, 45, 60]

    rows = []
    print(f"OpenCV {cv2.__version__}, marker {px}px, {TRIALS} trials per cell\n")
    print("wrap    " + "".join(f"{a:>7}°" for a in angles))
    for wrap in WRAP_FRACTIONS:
        cells = []
        for a in angles:
            rng = np.random.default_rng(int(wrap * 100) * 97 + a)
            hits = sum(detect(degrade(wrap_on_cylinder(marker, wrap, float(a)), rng))
                       for _ in range(TRIALS))
            rows.append({"wrap": wrap, "angle_deg": a, "detected": hits, "trials": TRIALS})
            cells.append(f"{hits:>8}")
        print(f"{wrap:>5.2f}   " + "".join(cells))

    print("\nwrap fraction for real containers:")
    for name, wrap in CONTAINERS.items():
        near = min(WRAP_FRACTIONS, key=lambda w: abs(w - wrap))
        at_zero = next(r["detected"] for r in rows if r["wrap"] == near and r["angle_deg"] == 0)
        print(f"  {name:24s} wrap≈{wrap:.2f}  (nearest measured {near:.2f}: {at_zero}/{TRIALS} head-on)")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "opencv": cv2.__version__,
        "marker_px": px,
        "trials_per_condition": TRIALS,
        "wrap_fractions": WRAP_FRACTIONS,
        "containers": CONTAINERS,
        "grid": rows,
        "caveat": "synthetic cylinder; no specular highlight, no motion blur",
    }, indent=1), encoding="utf-8")
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    main()
