"""Can an open fiducial marker be read the way NaviLens claims to be?

NaviLens is proprietary. The property that matters for a blind user is not the
payload but the *non-aim* read: the code is found without the camera being
pointed at it squarely, from a distance, at an angle. A plain QR code fails
there, which is why QR on packaging has never worked for blind shoppers.

ArUco markers ship with OpenCV and are free. This measures the two things that
decide whether they can stand in: how small the marker can get in frame before
detection fails, and how far off-axis the camera can be.

The test is synthetic — a rendered marker, scaled and warped, with noise and
blur. That overstates real-world performance, because it has no motion blur, no
specular highlights off a glossy bottle, and no rolling shutter. Treat the
numbers as an upper bound and the failure points as the informative part.

Usage:
    python scripts/marker_feasibility.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = PROJECT_ROOT / "docs" / "track-b-marker-measurements.json"

FRAME = (720, 1280)          # a phone camera frame, portrait-ish crop
DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 7
TRIALS = 12                  # noise seeds per condition


def render_marker(px: int) -> np.ndarray:
    img = cv2.aruco.generateImageMarker(cv2.aruco.getPredefinedDictionary(DICT), MARKER_ID, px)
    # Real markers are printed with a quiet zone; without it detection is unfair.
    pad = max(px // 8, 4)
    return cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)


def place(marker: np.ndarray, frame_shape: tuple[int, int], angle_deg: float) -> np.ndarray:
    """Drop the marker into a frame, rotated about its vertical axis."""
    h, w = frame_shape
    scene = np.full((h, w), 210, np.uint8)          # mid-grey background, like packaging
    mh, mw = marker.shape

    # Perspective warp: tilt about the vertical axis by angle_deg.
    t = np.radians(angle_deg)
    shrink = abs(np.cos(t))
    dx = mw * (1 - shrink) / 2
    src = np.float32([[0, 0], [mw, 0], [mw, mh], [0, mh]])
    dst = np.float32([
        [dx, mh * (1 - shrink) * 0.15],
        [mw - dx, 0],
        [mw - dx, mh],
        [dx, mh - mh * (1 - shrink) * 0.15],
    ])
    warped = cv2.warpPerspective(
        marker, cv2.getPerspectiveTransform(src, dst), (mw, mh),
        borderMode=cv2.BORDER_CONSTANT, borderValue=210,
    )

    y = (h - mh) // 2
    x = (w - mw) // 2
    scene[y : y + mh, x : x + mw] = warped
    return scene


def degrade(scene: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = cv2.GaussianBlur(scene, (3, 3), 0.8)
    noise = rng.normal(0, 6, out.shape)
    return np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def detect(scene: np.ndarray) -> bool:
    detector = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(DICT), cv2.aruco.DetectorParameters()
    )
    corners, ids, _ = detector.detectMarkers(scene)
    return ids is not None and MARKER_ID in ids.flatten()


def sweep_size() -> list[dict]:
    rows = []
    for px in [200, 140, 100, 72, 56, 44, 36, 28, 22, 18, 14, 12, 10]:
        rng = np.random.default_rng(px)
        hits = sum(detect(degrade(place(render_marker(px), FRAME, 0.0), rng)) for _ in range(TRIALS))
        frac = px / FRAME[1]
        rows.append({"marker_px": px, "frame_fraction": round(frac, 4), "detected": hits, "trials": TRIALS})
    return rows


def sweep_matrix() -> list[dict]:
    """Size against angle. The two trade off, and one number for either hides that."""
    rows = []
    for px in [200, 120, 72, 44, 24, 16]:
        marker = render_marker(px)
        for angle in [0, 15, 30, 45, 60, 70]:
            rng = np.random.default_rng(px * 100 + angle)
            hits = sum(detect(degrade(place(marker, FRAME, float(angle)), rng)) for _ in range(TRIALS))
            rows.append({"marker_px": px, "angle_deg": angle, "detected": hits, "trials": TRIALS})
    return rows


def sweep_angle(px: int) -> list[dict]:
    rows = []
    for angle in [0, 15, 30, 45, 55, 65, 70, 75, 80]:
        rng = np.random.default_rng(angle + 1000)
        hits = sum(detect(degrade(place(render_marker(px), FRAME, float(angle)), rng)) for _ in range(TRIALS))
        rows.append({"angle_deg": angle, "detected": hits, "trials": TRIALS})
    return rows


def main() -> None:
    print(f"OpenCV {cv2.__version__}, dictionary DICT_4X4_50, frame {FRAME[1]}x{FRAME[0]}\n")

    size_rows = sweep_size()
    print("marker size sweep (head-on):")
    print("  px   frame%   detected")
    smallest = None
    for r in size_rows:
        ok = r["detected"] == r["trials"]
        if ok:
            smallest = r
        print(f"  {r['marker_px']:>3}  {r['frame_fraction']*100:5.1f}%   {r['detected']}/{r['trials']}"
              f"{'' if ok else '   <- degraded'}")

    px = smallest["marker_px"] if smallest else 100
    angle_rows = sweep_angle(px)
    print(f"\nangle sweep at {px}px:")
    print("  deg  detected")
    widest = None
    for r in angle_rows:
        ok = r["detected"] == r["trials"]
        if ok:
            widest = r
        print(f"  {r['angle_deg']:>3}   {r['detected']}/{r['trials']}{'' if ok else '   <- degraded'}")

    matrix = sweep_matrix()
    print(chr(10) + "size x angle (detections out of %d):" % TRIALS)
    angles = sorted({r["angle_deg"] for r in matrix})
    print("  px  " + "".join(f"{a:>6}" for a in angles))
    for px in sorted({r["marker_px"] for r in matrix}, reverse=True):
        cells = []
        for a in angles:
            hit = next(r["detected"] for r in matrix if r["marker_px"] == px and r["angle_deg"] == a)
            cells.append(f"{hit:>6}")
        print(f"  {px:>3} " + "".join(cells))

    result = {
        "size_angle_matrix": matrix,
        "opencv": cv2.__version__,
        "dictionary": "DICT_4X4_50",
        "frame": {"w": FRAME[1], "h": FRAME[0]},
        "trials_per_condition": TRIALS,
        "size_sweep": size_rows,
        "angle_sweep": angle_rows,
        "smallest_reliable_px": smallest["marker_px"] if smallest else None,
        "smallest_reliable_frame_fraction": smallest["frame_fraction"] if smallest else None,
        "widest_reliable_angle_deg": widest["angle_deg"] if widest else None,
        "caveat": "synthetic: no motion blur, no specular highlight, no rolling shutter",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"\n-> {OUT_JSON}")


if __name__ == "__main__":
    main()
