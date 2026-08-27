"""Measure ArUco detection from a phone video sweep, not from posed stills.

The synthetic study (`marker_feasibility.py`) bounds detection against marker
size and camera angle, and says plainly that it overstates the real world
because it has no motion blur, no specular highlight off a glossy bottle and no
rolling shutter. Those three are what a real shoot is for.

The obvious plan — a factorial of distances, angles, lightings and exposures,
sixty frames a container — is the wrong medium for two of the three. Motion blur
and rolling shutter exist only while the camera is moving. Posing for each of
480 stills removes exactly the artefacts the shoot was meant to introduce, and
costs an afternoon to do it.

A sweep records them for free. Walk the camera around the container while
filming and every frame carries the blur that a hand actually produces at that
moment. Twenty seconds at 30 fps is 600 frames, and the angle varies
continuously rather than at five levels, so the result is a curve rather than
five points on one.

The difficulty a sweep creates is knowing the camera angle for each frame.
Recovering it from the container's own marker is circular: it works only where
detection worked, so precisely the failures — the data — have no angle. Hence
the reference marker. A large flat marker beside the container, seen at a
shallow enough angle to stay readable throughout, gives camera pose on every
frame including the ones where the container's marker is lost.

Shooting, per container, four sweeps: indoor diffuse and direct light, each at
auto exposure and at -2 EV. Eight minutes of recording covers six containers.

Usage:
    python scripts/marker_video_eval.py shoot/*.mp4 --ref-id 0 --ref-mm 100
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "docs" / "marker-video-eval.json"

DICT = cv2.aruco.DICT_4X4_50


def detector():
    params = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(DICT), params)


def camera_matrix(w: int, h: int) -> np.ndarray:
    """A phone-shaped guess, good enough for an angle to a few degrees.

    Calibrating the specific handset would be better and is a half-hour with a
    checkerboard. It is not done here because the angle only has to be accurate
    enough to place a frame in a bin, and a 60-degree field of view is right for
    a phone's main camera to within a couple of degrees.
    """
    f = 0.5 * w / math.tan(math.radians(60) / 2)
    return np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]], dtype=float)


def obj_points(size_mm: float) -> np.ndarray:
    h = size_mm / 2
    return np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]], dtype=float)


def angle_from_pose(rvec: np.ndarray) -> float:
    """Degrees between the camera axis and the reference marker's normal."""
    r, _ = cv2.Rodrigues(rvec)
    normal = r @ np.array([0.0, 0.0, 1.0])
    cos = abs(float(normal[2])) / (np.linalg.norm(normal) or 1.0)
    return math.degrees(math.acos(min(1.0, max(-1.0, cos))))


def blurriness(gray: np.ndarray) -> float:
    """Variance of the Laplacian: low means the frame is blurred.

    Reported rather than thresholded. Whether a blurred frame should count as a
    detection failure is the reader's question, not this script's — a frame too
    blurred for a person to read is not evidence against the marker.
    """
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def scan(path: Path, ref_id: int, ref_mm: float, target_id: int | None,
         stride: int) -> list[dict]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise SystemExit(f"cannot open {path}")
    det = detector()
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    K = camera_matrix(w, h)
    dist = np.zeros(5)

    rows: list[dict] = []
    index = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        index += 1
        if index % stride:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = det.detectMarkers(gray)
        found = {int(i) for i in ids.flatten()} if ids is not None else set()

        angle = None
        if ref_id in found:
            c = corners[list(ids.flatten()).index(ref_id)][0].astype(float)
            ok_pnp, rvec, _ = cv2.solvePnP(obj_points(ref_mm), c, K, dist,
                                           flags=cv2.SOLVEPNP_IPPE_SQUARE)
            if ok_pnp:
                angle = round(angle_from_pose(rvec), 1)

        # Whatever is not the reference is the container's marker. Naming it is
        # optional so a shoot does not have to record which ID went on which
        # bottle.
        targets = found - {ref_id}
        hit = (target_id in found) if target_id is not None else bool(targets)

        # How much of the frame width the marker spans is the axis the synthetic
        # study used, so it is measured the same way here.
        span = None
        if targets:
            tid = target_id if target_id in found else sorted(targets)[0]
            c = corners[list(ids.flatten()).index(tid)][0]
            span = round(float(np.ptp(c[:, 0])) / w, 4)

        rows.append({
            "video": path.name,
            "frame": index,
            "detected": hit,
            "angle_deg": angle,
            "width_fraction": span,
            "blur": round(blurriness(gray), 1),
            "mean_luma": round(float(gray.mean()), 1),
            # The brightest patch is the specular highlight, and the synthetic
            # sweep predicted detection turns over on its peak rather than on
            # the light's angular size. This is the column that tests it.
            "peak_luma": round(float(np.percentile(gray, 99.9)), 1),
        })
    cap.release()
    return rows


def summarise(rows: list[dict]) -> dict:
    bins: dict[str, dict] = {}
    for r in rows:
        a = r["angle_deg"]
        if a is None:
            continue
        key = f"{int(a // 15) * 15}-{int(a // 15) * 15 + 15}"
        b = bins.setdefault(key, {"frames": 0, "detected": 0})
        b["frames"] += 1
        b["detected"] += bool(r["detected"])
    for b in bins.values():
        b["rate"] = round(b["detected"] / b["frames"], 4)
    placed = sum(1 for r in rows if r["angle_deg"] is not None)
    return {
        "frames": len(rows),
        "frames_with_angle": placed,
        "detected": sum(1 for r in rows if r["detected"]),
        "by_angle": dict(sorted(bins.items(), key=lambda kv: int(kv[0].split("-")[0]))),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--ref-id", type=int, default=0,
                    help="the flat reference marker beside the container")
    ap.add_argument("--ref-mm", type=float, default=100.0)
    ap.add_argument("--target-id", type=int, default=None,
                    help="the marker on the container; omit to take any other")
    ap.add_argument("--stride", type=int, default=2,
                    help="keep every Nth frame; consecutive frames are near-duplicates")
    args = ap.parse_args()

    paths = [Path(p) for p in args.videos]
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"no such file: {missing[0]}")

    rows: list[dict] = []
    for path in paths:
        got = scan(path, args.ref_id, args.ref_mm, args.target_id, args.stride)
        rows.extend(got)
        hit = sum(1 for r in got if r["detected"])
        print(f"{path.name:32s} {len(got):>6,} frames  {hit:>6,} detected "
              f"({hit / max(1, len(got)):.1%})", flush=True)

    summary = summarise(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"summary": summary, "frames": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{summary['frames']:,} frames, "
          f"{summary['frames_with_angle']:,} placed on the angle axis")
    for k, v in summary["by_angle"].items():
        print(f"  {k + '°':>9s} {v['detected']:>6,}/{v['frames']:<6,} {v['rate']:>7.1%}")
    if summary["frames_with_angle"] < summary["frames"]:
        lost = summary["frames"] - summary["frames_with_angle"]
        print(f"\n  {lost:,} frames carry no angle: the reference marker was not "
              f"visible. They are kept but cannot be placed on the curve.")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
